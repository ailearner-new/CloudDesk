#!/usr/bin/env python
"""Smoke test for CloudDesk API.

Run against a live deployment:
    BASE_URL=http://localhost:8000 python scripts/smoke_test.py

Or set BASE_URL environment variable.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def run_smoke(base_url: str) -> bool:
    """Run smoke tests against the API."""
    print(f"Running smoke tests against {base_url}")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # Test health endpoints
        tests = [
            ("GET", "/health", 200, "Health check"),
            ("GET", "/health/live", 200, "Liveness probe"),
            ("GET", "/health/ready", 200, "Readiness probe"),
        ]

        all_passed = True
        for method, path, expected_status, name in tests:
            try:
                resp = await client.request(method, path)
                status = "PASS" if resp.status_code == expected_status else "FAIL"
                if resp.status_code != expected_status:
                    all_passed = False
                print(f"  {status} {name}: {method} {path} -> {resp.status_code}")
            except Exception as e:
                print(f"  FAIL {name}: {method} {path} -> {e}")
                all_passed = False

        # Test agents endpoint
        try:
            resp = await client.get("/api/v1/agents")
            if resp.status_code == 200:
                data = resp.json()
                nodes = data.get("nodes", [])
                print(f"  PASS Agents endpoint: {len(nodes)} nodes")
            else:
                print(f"  FAIL Agents endpoint: {resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  FAIL Agents endpoint: {e}")
            all_passed = False

        # Test tickets list
        try:
            resp = await client.get("/api/v1/tickets")
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                print(f"  PASS Tickets list: {len(items)} tickets")
            else:
                print(f"  FAIL Tickets list: {resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  FAIL Tickets list: {e}")
            all_passed = False

        # Test customers list
        try:
            resp = await client.get("/api/v1/customers")
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                print(f"  PASS Customers list: {len(items)} customers")
            else:
                print(f"  FAIL Customers list: {resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  FAIL Customers list: {e}")
            all_passed = False

        # Test knowledge articles
        try:
            resp = await client.get("/api/v1/knowledge/articles")
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                print(f"  PASS Knowledge articles: {len(items)} articles")
            else:
                print(f"  FAIL Knowledge articles: {resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  FAIL Knowledge articles: {e}")
            all_passed = False

        print("=" * 60)
        if all_passed:
            print("ALL SMOKE TESTS PASSED")
        else:
            print("SOME SMOKE TESTS FAILED")
        return all_passed


def main():
    parser = argparse.ArgumentParser(description="CloudDesk smoke test")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"),
                        help="Base URL of the API (default: http://localhost:8000)")
    args = parser.parse_args()

    success = asyncio.run(run_smoke(args.base_url))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()