#!/usr/bin/env python3
"""Register one reviewed production manifest as a pending Central node."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is missing")
    return value


def request_json(url: str, method: str, payload: dict | None, token: str) -> tuple[int, dict]:
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(url, data=body, method=method)
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request, timeout=15) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        try:
            detail = json.load(error)
            message = detail.get("message") or detail.get("error") or "request rejected"
        except Exception:
            message = "request rejected"
        raise RuntimeError(f"{method} {url} returned HTTP {error.code}: {message}") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"{method} {url} failed: {error}") from error


def send_key_email(api_key: str, node_id: str, recipient: str, central_url: str) -> None:
    sendgrid_key = required_env("SENDGRID_API_KEY")
    sender = required_env("KEY_DELIVERY_FROM_EMAIL")
    text = f"""Your Little Linked Librarian node manifest has been merged and registered as pending.

Node ID: {node_id}
Central URL: {central_url}
One-time node API key: {api_key}

Store the key only in your node's private runtime environment:

DISCOVERY_ENABLED=true
CENTRAL_BASE_URL={central_url}
CENTRAL_NODE_ID={node_id}
CENTRAL_NODE_API_KEY=<the key above>
CENTRAL_HEARTBEAT_INTERVAL_SECONDS=300

Restart the node and reply through the reviewed registration channel when its heartbeat is running. Central activation remains a separate human approval step. This key will not be shown in GitHub or the registry manifest.
"""
    payload = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": sender},
        "subject": f"LLL node credential for {node_id}",
        "content": [{"type": "text/plain", "value": text}],
    }
    request = Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {sendgrid_key}",
            "Content-Type": "application/json",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=15) as response:
                if response.status != 202:
                    raise RuntimeError(f"SendGrid returned HTTP {response.status}")
                return
        except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError("Credential delivery failed after three attempts; the node remains pending and requires administrator-assisted key recovery") from last_error


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/register_node.py nodes/<node-id>.yaml", file=sys.stderr)
        return 2
    if os.environ.get("GITHUB_ACTIONS") != "true" and os.environ.get("ALLOW_LOCAL_CENTRAL_REGISTRATION") != "true":
        print("Refusing Central mutation outside trusted automation; set ALLOW_LOCAL_CENTRAL_REGISTRATION=true only in a protected admin environment", file=sys.stderr)
        return 2

    manifest = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if manifest["metadata"]["labels"]["environment"] != "production":
        print(f"SKIP {sys.argv[1]}: not a production manifest")
        return 0

    central_url = required_env("CENTRAL_API_URL").rstrip("/")
    admin_token = required_env("CENTRAL_ADMIN_TOKEN")
    required_env("SENDGRID_API_KEY")
    required_env("KEY_DELIVERY_FROM_EMAIL")
    spec = manifest["spec"]
    node_id = manifest["metadata"]["name"]
    location = spec["location"]
    coordinates = location.get("coordinates")
    payload = {
        "nodeId": node_id,
        "displayName": spec["displayName"],
        "endpoint": spec["connectivity"]["endpoint"],
        "connectivityType": spec["connectivity"]["type"],
        "operatorEmail": spec["operator"]["email"],
        "operatorUserId": spec["operator"]["centralUserId"],
        "locationDescription": location["description"],
    }
    if coordinates:
        payload.update(latitude=coordinates["latitude"], longitude=coordinates["longitude"])

    status, response = request_json(f"{central_url}/api/admin/network/nodes", "POST", payload, admin_token)
    if status != 201 or response.get("node", {}).get("status") != "pending":
        raise RuntimeError("Central did not create the expected pending node")
    api_key = response.get("apiKey", "")
    if not api_key:
        raise RuntimeError("Central created the node but did not return its one-time key")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::add-mask::{api_key}")

    if spec["privacyTier"] != "public" or spec.get("allowedUsers"):
        settings = {
            "privacyTier": spec["privacyTier"],
            "allowedUsers": spec.get("allowedUsers", []),
        }
        request_json(
            f"{central_url}/api/network/nodes/{quote(node_id, safe='')}/settings",
            "PATCH",
            settings,
            api_key,
        )

    send_key_email(api_key, node_id, spec["operator"]["email"], central_url)
    print(f"Registered {node_id} as pending and accepted credential delivery for the reviewed operator email.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
