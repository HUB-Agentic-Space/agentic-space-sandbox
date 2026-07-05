#!/usr/bin/env python3
"""parse-feed — Parse and display RSS/Atom feed entries.

Usage:
    parse-feed <feed_url_or_file> [--limit N] [--format json|text|csv] [--output file]
"""
import argparse
import csv
import io
import json
import sys

import feedparser


def parse_feed(source: str, limit: int = 0) -> dict:
    if source.startswith("http://") or source.startswith("https://"):
        parsed = feedparser.parse(source)
    else:
        with open(source, "r", encoding="utf-8") as f:
            parsed = feedparser.parse(f.read())

    feed_info = {
        "title": parsed.feed.get("title", ""),
        "link": parsed.feed.get("link", ""),
        "description": parsed.feed.get("description", ""),
        "entries": [],
    }

    entries = parsed.entries[:limit] if limit > 0 else parsed.entries
    for entry in entries:
        feed_info["entries"].append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "updated": entry.get("updated", ""),
            "summary": entry.get("summary", "")[:500],
            "author": entry.get("author", ""),
            "id": entry.get("id", ""),
            "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
        })

    return feed_info


def main():
    parser = argparse.ArgumentParser(description="Parse and display RSS/Atom feed entries")
    parser.add_argument("source", help="Feed URL or local file path")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit number of entries (0 = all)")
    parser.add_argument("--format", choices=["json", "text", "csv"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    args = parser.parse_args()

    result = parse_feed(args.source, args.limit)

    if args.format == "json":
        output = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["title", "link", "published", "author", "summary"])
        writer.writeheader()
        for entry in result["entries"]:
            writer.writerow({k: entry.get(k, "") for k in ["title", "link", "published", "author", "summary"]})
        output = buf.getvalue()
    else:
        lines = [f"Feed: {result['title']}", f"Link: {result['link']}", f"Description: {result['description']}", ""]
        for i, entry in enumerate(result["entries"], 1):
            lines.append(f"--- Entry {i} ---")
            lines.append(f"  Title: {entry['title']}")
            lines.append(f"  Link: {entry['link']}")
            lines.append(f"  Published: {entry['published']}")
            lines.append(f"  Author: {entry['author']}")
            lines.append(f"  Summary: {entry['summary'][:200]}...")
            if entry["tags"]:
                lines.append(f"  Tags: {', '.join(entry['tags'])}")
            lines.append("")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
