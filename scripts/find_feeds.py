#!/usr/bin/env python3
"""find-feeds — Discover RSS/Atom feeds on a webpage.

Usage:
    find-feeds <url> [--output file] [--check]
"""
import argparse
import json
import re
import sys

import requests
from bs4 import BeautifulSoup


FEED_TYPES = ["application/rss+xml", "application/atom+xml", "application/json", "text/xml"]
FEED_PATTERNS = re.compile(
    r"(feed|rss|atom|\.xml|\.rss|/feed|/rss|/atom)", re.IGNORECASE
)


def discover_feeds(url: str, check: bool = False) -> list:
    headers = {"User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"}
    resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    feeds = set()

    # 1. <link> tags with feed types
    for link in soup.find_all("link", attrs={"type": True}):
        if link.get("type") in FEED_TYPES:
            href = link.get("href", "")
            if href:
                feeds.add(requests.compat.urljoin(url, href))

    # 2. <a> tags pointing to feed-like URLs
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if FEED_PATTERNS.search(href):
            feeds.add(requests.compat.urljoin(url, href))

    # 3. Common feed paths
    from urllib.parse import urlsplit, urlunsplit
    parts = urlsplit(url)
    base = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    for path in ["/feed", "/feed/", "/rss", "/rss.xml", "/atom.xml",
                 "/feeds/all.atom.xml", "/index.xml", "/blog/feed",
                 "/blog/rss.xml", "/rss/feed"]:
        candidate = base + path
        if check:
            try:
                r = requests.head(candidate, headers=headers, timeout=10, allow_redirects=True)
                if r.status_code == 200:
                    feeds.add(str(r.url))
            except requests.RequestException:
                pass
        else:
            feeds.add(candidate)

    return sorted(feeds)


def main():
    parser = argparse.ArgumentParser(description="Discover RSS/Atom feeds on a webpage")
    parser.add_argument("url", help="Target URL to scan for feeds")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--check", action="store_true",
                        help="Verify feed URLs are reachable (HEAD requests)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    feeds = discover_feeds(args.url, check=args.check)

    if args.format == "json":
        output = json.dumps({"url": args.url, "feeds": feeds}, ensure_ascii=False, indent=2)
    else:
        if not feeds:
            output = f"No feeds found at {args.url}"
        else:
            lines = [f"Feeds found at {args.url}:", ""]
            for i, feed in enumerate(feeds, 1):
                lines.append(f"  {i}. {feed}")
            output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
