#!/usr/bin/env python3
"""Verify the six anonymous LLL Lite 0.1.0 routes on one live node."""

from __future__ import annotations

import json
import ipaddress
import socket
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

import yaml


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def require_public_host(hostname: str) -> None:
    addresses = {item[4][0] for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)}
    if not addresses:
        raise RuntimeError(f"{hostname} did not resolve")
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if not address.is_global:
            raise RuntimeError(f"{hostname} resolved to a private or non-global address")


def get_json(base: str, path: str) -> object:
    url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    hostname = urlparse(url).hostname
    if not hostname:
        raise RuntimeError(f"GET {path} produced an invalid URL")
    require_public_host(hostname)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "lll-node-conformance/0.1.0"})
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), RejectRedirects())
    try:
        with opener.open(request, timeout=8) as response:
            if response.status != 200:
                raise RuntimeError(f"GET {path} returned HTTP {response.status}")
            if "application/json" not in response.headers.get("content-type", ""):
                raise RuntimeError(f"GET {path} did not return JSON")
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"GET {path} failed: {error}") from error


def data_array(value: object, path: str) -> list:
    if not isinstance(value, dict) or not isinstance(value.get("data"), list):
        raise RuntimeError(f"{path} must return a data array")
    if len(value["data"]) > 25:
        raise RuntimeError(f"{path} exceeded the requested bound")
    return value["data"]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/verify_live_node.py nodes/<node-id>.yaml", file=sys.stderr)
        return 2
    manifest = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    base = manifest["spec"]["connectivity"]["apiBaseUrl"]
    if not base.startswith("https://"):
        print("Live verification requires an HTTPS apiBaseUrl", file=sys.stderr)
        return 2

    health = get_json(base, "/health")
    if not isinstance(health, dict) or health.get("status") != "ok":
        raise RuntimeError("/health must report status=ok")
    print("PASS /health")

    boxes = data_array(get_json(base, "/api/boxes?limit=25"), "/api/boxes")
    books = data_array(get_json(base, "/api/books?limit=25"), "/api/books")
    print("PASS /api/boxes")
    print("PASS /api/books")

    if boxes:
        box_id = str(boxes[0].get("id", ""))
        if not box_id:
            raise RuntimeError("box list item is missing id")
        get_json(base, f"/api/boxes/{quote(box_id, safe='')}")
        data_array(get_json(base, f"/api/boxes/{quote(box_id, safe='')}/books?limit=25"), "/api/boxes/{id}/books")
        print("PASS /api/boxes/{id}")
        print("PASS /api/boxes/{id}/books")
    else:
        print("SKIP detail box routes: public box list is empty")

    if books:
        book_id = str(books[0].get("id", ""))
        if not book_id:
            raise RuntimeError("book list item is missing id")
        get_json(base, f"/api/books/{quote(book_id, safe='')}")
        print("PASS /api/books/{id}")
    else:
        print("SKIP /api/books/{id}: public book list is empty")

    print(f"Live LLL Lite 0.1.0 compatibility check passed for {base}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
