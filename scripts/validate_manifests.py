#!/usr/bin/env python3
"""Validate secret-free LLL node manifests without contacting a node."""

from __future__ import annotations

import ipaddress
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
NODE_ID = re.compile(r"^lll-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
SECRET_KEY = re.compile(r"(?:api.?key|token|secret|password|private.?key|database.?url|tunnel.?credential)", re.I)
SECRET_VALUE = re.compile(
    r"(?:-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|"
    r"sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"
)
CAPABILITIES = {"health", "boxes", "books", "box-inventory"}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError("manifest must be an object")
    return value


def scan_secrets(value: object, field: str = "manifest") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SECRET_KEY.search(str(key)):
                raise ValueError(f"{field}.{key} uses a forbidden credential field name")
            scan_secrets(child, f"{field}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_secrets(child, f"{field}[{index}]")
    elif isinstance(value, str) and SECRET_VALUE.search(value):
        raise ValueError(f"{field} contains a credential-like value")


def parse_origin(raw: str, field: str, production: bool) -> str:
    parsed = urlparse(raw)
    allowed = {"https"} if production else {"http", "https"}
    if parsed.scheme not in allowed or not parsed.hostname:
        raise ValueError(f"{field} must be a valid {'HTTPS' if production else 'HTTP(S)'} origin")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"{field} must not contain credentials, query, or fragment")
    if parsed.path not in ("", "/"):
        raise ValueError(f"{field} must be an origin without a path")
    if production:
        if parsed.hostname.lower() == "localhost":
            raise ValueError(f"{field} must not target localhost")
        try:
            address = ipaddress.ip_address(parsed.hostname)
            if not address.is_global:
                raise ValueError(f"{field} must not target a private or non-global address")
        except ValueError as error:
            if "must not target" in str(error):
                raise
    default_port = 443 if parsed.scheme == "https" else 80
    port = f":{parsed.port}" if parsed.port and parsed.port != default_port else ""
    return f"{parsed.scheme}://{parsed.hostname.lower()}{port}"


def validate_one(path: Path, schema: dict, example: bool = False) -> dict:
    document = load_yaml(path)
    scan_secrets(document)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or 'manifest'}: {error.message}" for error in errors
        )
        raise ValueError(details)

    node_id = document["metadata"]["name"]
    if not NODE_ID.fullmatch(node_id):
        raise ValueError("metadata.name is invalid")
    if not example and path.name != f"{node_id}.yaml":
        raise ValueError(f"filename must be {node_id}.yaml")

    labels = document["metadata"]["labels"]
    production = labels["environment"] == "production"
    operator = document["spec"]["operator"]
    if not EMAIL.fullmatch(operator["email"]):
        raise ValueError("spec.operator.email is invalid")
    if production:
        central_user_id = operator.get("centralUserId", "")
        if not central_user_id:
            raise ValueError("production manifests require spec.operator.centralUserId")
        if not example and central_user_id.startswith("replace-"):
            raise ValueError("replace the example Central account ID")

    connection = document["spec"]["connectivity"]
    origins = {
        key: parse_origin(connection[key], f"spec.connectivity.{key}", production)
        for key in ("endpoint", "uiUrl", "apiBaseUrl")
    }
    if production and len(set(origins.values())) != 1:
        raise ValueError("production endpoint, uiUrl, and apiBaseUrl must currently share one origin")

    compatibility = document["spec"]["compatibility"]
    if set(compatibility["capabilities"]) != CAPABILITIES:
        raise ValueError(f"capabilities must contain exactly {', '.join(sorted(CAPABILITIES))}")

    consent = document["spec"]["consent"]
    coordinates = document["spec"]["location"].get("coordinates")
    if production and not consent["publishCatalog"]:
        raise ValueError("production registration requires publishCatalog consent")
    if production and coordinates and not consent["publishLocation"]:
        raise ValueError("coordinates require publishLocation consent")

    return {
        "id": node_id,
        "endpoint": origins["endpoint"],
        "environment": labels["environment"],
        "example": example,
    }


def main() -> int:
    schema = json.loads((ROOT / "schemas/node-manifest.schema.json").read_text(encoding="utf-8"))
    paths = [Path(argument).resolve() for argument in sys.argv[1:]]
    if not paths:
        paths = sorted((ROOT / "nodes").glob("*.yaml")) + sorted((ROOT / "examples").glob("*.yaml"))
    if not paths:
        print("No manifests found", file=sys.stderr)
        return 1

    results: list[dict] = []
    failures: list[str] = []
    for path in paths:
        try:
            result = validate_one(path, schema, example=path.parent.name == "examples")
            results.append(result)
            print(f"PASS {path.relative_to(ROOT)}")
        except Exception as error:  # validation must report all files in one run
            failures.append(f"{path}: {error}")

    production = [result for result in results if result["environment"] == "production" and not result["example"]]
    for field in ("id", "endpoint"):
        values = [result[field] for result in production]
        duplicates = sorted({value for value in values if values.count(value) > 1})
        failures.extend(f"duplicate production {field}: {value}" for value in duplicates)

    if failures:
        print("\n".join(f"FAIL {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Validated {len(results)} manifest(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
