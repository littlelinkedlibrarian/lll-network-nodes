#!/usr/bin/env python3
"""Approve a pending Central node only after a recent healthy heartbeat."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is missing")
    return value


def central_json(url: str, method: str, token: str) -> dict:
    request = Request(url, method=method, headers={"Accept": "application/json", "Authorization": f"Bearer {token}"})
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"{method} {url} returned HTTP {error.code}") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"{method} {url} failed: {error}") from error


def parse_time(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/approve_node.py lll-node-id", file=sys.stderr)
        return 2
    if os.environ.get("GITHUB_ACTIONS") != "true" and os.environ.get("ALLOW_LOCAL_CENTRAL_APPROVAL") != "true":
        print("Refusing Central approval outside trusted automation; set ALLOW_LOCAL_CENTRAL_APPROVAL=true only in a protected admin environment", file=sys.stderr)
        return 2

    node_id = sys.argv[1]
    manifest_path = Path("nodes") / f"{node_id}.yaml"
    if not manifest_path.is_file():
        raise RuntimeError(f"Reviewed manifest {manifest_path} does not exist")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest["metadata"]["labels"]["environment"] != "production":
        raise RuntimeError("Only production manifests can be approved")

    central_url = required_env("CENTRAL_API_URL").rstrip("/")
    token = required_env("CENTRAL_ADMIN_TOKEN")
    query = urlencode({"search": node_id, "limit": 100})
    result = central_json(f"{central_url}/api/admin/network/nodes?{query}", "GET", token)
    matches = [node for node in result.get("data", []) if node.get("nodeId") == node_id]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one Central record for {node_id}, found {len(matches)}")
    node = matches[0]
    if node.get("status") != "pending":
        raise RuntimeError(f"Node must be pending, not {node.get('status')}")
    if node.get("healthCheckFailures", 0) != 0:
        raise RuntimeError("Node has recorded health-check failures")
    if not node.get("lastSeen"):
        raise RuntimeError("Node has not sent a heartbeat")
    age = (datetime.now(timezone.utc) - parse_time(node["lastSeen"])).total_seconds()
    if age < 0 or age > 900:
        raise RuntimeError(f"Node heartbeat is not recent ({round(age)} seconds old)")
    if node.get("endpoint", "").rstrip("/") != manifest["spec"]["connectivity"]["endpoint"].rstrip("/"):
        raise RuntimeError("Central endpoint does not match the reviewed manifest")

    response = central_json(
        f"{central_url}/api/admin/network/nodes/{quote(node_id, safe='')}/approve",
        "POST",
        token,
    )
    if response.get("node", {}).get("status") != "active":
        raise RuntimeError("Central did not return active status")
    print(f"Approved {node_id}; Central now reports it active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
