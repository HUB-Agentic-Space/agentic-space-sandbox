#!/usr/bin/env python3
"""api-fetch — Fetch a JSON API and optionally filter with jq-like syntax.

Usage:
    api-fetch <url> [jq_filter] [--headers key=val ...] [--output file]
"""
import argparse
import json
import subprocess
import sys

import requests


def main():
    parser = argparse.ArgumentParser(description="Fetch JSON API and filter with jq")
    parser.add_argument("url", help="API URL")
    parser.add_argument("jq_filter", nargs="?", default=None, help="jq filter expression")
    parser.add_argument("--header", "-H", action="append", default=[],
                        help="Custom header (key=value), repeatable")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    headers = {"Accept": "application/json",
               "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"}
    for h in args.header:
        if "=" in h:
            k, v = h.split("=", 1)
            headers[k.strip()] = v.strip()

    resp = requests.get(args.url, headers=headers, timeout=args.timeout)
    resp.raise_for_status()

    data = resp.text

    if args.jq_filter:
        try:
            result = subprocess.run(
                ["jq", args.jq_filter],
                input=data,
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            print(f"jq error: {e.stderr}", file=sys.stderr)
            output = data
    else:
        # Pretty-print JSON
        try:
            parsed = json.loads(data)
            output = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            output = data

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
