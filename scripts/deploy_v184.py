#!/usr/bin/env python3
"""Check or redeploy the pinned POT BREAKER Cloudflare Worker v184.

This script restores an existing Cloudflare version; it does NOT build from
the repository's older Python/HTML sources.
"""
import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

WORKER = "potbreaker"
VERSION_NUMBER = 184
VERSION_ID = "ec53a477-dcef-4b75-8142-8066aabf1fe6"


def api(method, path, payload=None):
    account = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not account or not token:
        raise RuntimeError("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=30) as response:
            obj = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"Cloudflare HTTP {error.code}: {error.read().decode('utf-8', 'replace')[:500]}") from error
    except URLError as error:
        raise RuntimeError(f"Cloudflare connection failed: {error.reason}") from error
    if not obj.get("success"):
        raise RuntimeError(f"Cloudflare API error: {obj.get('errors')}")
    return obj["result"]


def active_deployment():
    result = api("GET", f"/workers/scripts/{WORKER}/deployments?per_page=1")
    deployments = result.get("deployments", [])
    if not deployments:
        raise RuntimeError("No production deployment found")
    return deployments[0]


def is_pinned(deployment):
    return len(deployment.get("versions", [])) == 1 and (
        deployment["versions"][0].get("version_id") == VERSION_ID
        and deployment["versions"][0].get("percentage") == 100
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy", action="store_true", help="Deploy v184 to 100% traffic")
    args = parser.parse_args()

    version = api("GET", f"/workers/scripts/{WORKER}/versions/{VERSION_ID}")
    if version.get("id") != VERSION_ID or version.get("number") != VERSION_NUMBER:
        raise RuntimeError("Cloudflare version identity does not match v184")

    current = active_deployment()
    if args.deploy and not is_pinned(current):
        api("POST", f"/workers/scripts/{WORKER}/deployments", {
            "strategy": "percentage",
            "versions": [{"version_id": VERSION_ID, "percentage": 100}],
            "annotations": {"workers/message": "Deploy pinned production v184 from GitHub baseline"},
        })
        current = active_deployment()

    if not is_pinned(current):
        print("NOT ALIGNED: production is not 100% on v184", file=sys.stderr)
        return 2
    print(f"ALIGNED: {WORKER} v184 (100%), deployment {current.get('id')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
