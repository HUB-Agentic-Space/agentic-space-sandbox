#!/usr/bin/env python3
"""scrape-url — Fetch a URL and optionally extract content via CSS selector.

Usage:
    scrape-url <url> [css_selector] [--format text|html|json] [--output file]
"""
import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser(description="Fetch URL and extract content via CSS selector")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("selector", nargs="?", default=None, help="CSS selector to extract")
    parser.add_argument("--format", choices=["text", "html", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--user-agent", "-u", default=None, help="Custom User-Agent string")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    headers = {"User-Agent": args.user_agent or "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"}
    resp = requests.get(args.url, headers=headers, timeout=args.timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    if args.selector:
        elements = soup.select(args.selector)
        if args.format == "html":
            result = "\n".join(str(el) for el in elements)
        elif args.format == "json":
            result = json.dumps(
                [{"tag": el.name, "text": el.get_text(strip=True), "html": str(el)} for el in elements],
                ensure_ascii=False, indent=2
            )
        else:
            result = "\n".join(el.get_text(strip=True) for el in elements)
    else:
        if args.format == "html":
            result = str(soup)
        elif args.format == "json":
            result = json.dumps(
                {"title": soup.title.string if soup.title else "",
                 "text": soup.get_text(strip=True)[:5000]},
                ensure_ascii=False, indent=2
            )
        else:
            result = soup.get_text(separator="\n", strip=True)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
