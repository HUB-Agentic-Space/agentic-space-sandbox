#!/usr/bin/env python3
"""extract-data — Extract structured data from a webpage (JSON-LD, OpenGraph, meta tags).

Usage:
    extract-data <url> [--format json|text] [--output file]
"""
import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup
import extruct


def main():
    parser = argparse.ArgumentParser(description="Extract structured data (JSON-LD, OG, meta) from URL")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    headers = {"User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"}
    resp = requests.get(args.url, headers=headers, timeout=args.timeout)
    resp.raise_for_status()

    data = extruct.extract(resp.text, base_url=args.url, uniform=True,
                           syntaxes=["json-ld", "opengraph", "microdata", "microformat", "rdfa"])

    soup = BeautifulSoup(resp.text, "lxml")
    meta_tags = {}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")
        if name and content:
            meta_tags[name] = content

    result = {
        "url": args.url,
        "title": soup.title.string if soup.title else "",
        "meta": meta_tags,
        "structured_data": data,
    }

    if args.format == "text":
        lines = [f"URL: {result['url']}", f"Title: {result['title']}", "", "Meta Tags:"]
        for k, v in result["meta"].items():
            lines.append(f"  {k}: {v}")
        for syntax, items in result["structured_data"].items():
            if items:
                lines.append(f"\n{syntax}:")
                lines.append(json.dumps(items, ensure_ascii=False, indent=2))
        output = "\n".join(lines)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
