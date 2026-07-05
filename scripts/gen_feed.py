#!/usr/bin/env python3
"""gen-feed — Generate an RSS 2.0 feed from a JSON file.

Expected JSON format:
    {
        "title": "My Feed",
        "link": "https://example.com",
        "description": "Feed description",
        "entries": [
            {
                "title": "Entry title",
                "link": "https://example.com/1",
                "description": "Entry content",
                "published": "2024-01-01T00:00:00Z"
            }
        ]
    }

Usage:
    gen-feed <json_file> [--output file.rss]
"""
import argparse
import json
import sys

from feedgenerator import Rss201rev2Feed


def main():
    parser = argparse.ArgumentParser(description="Generate RSS 2.0 feed from JSON data")
    parser.add_argument("json_file", help="Path to JSON file with feed data")
    parser.add_argument("--output", "-o", default=None, help="Output RSS file (default: stdout)")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    feed = Rss201rev2Feed(
        title=data.get("title", "Generated Feed"),
        link=data.get("link", ""),
        description=data.get("description", ""),
        language=data.get("language", "en"),
    )

    for entry in data.get("entries", []):
        feed.add_item(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            description=entry.get("description", ""),
            pubdate=entry.get("published"),
            author_name=entry.get("author", ""),
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            feed.write(f, "utf-8")
        print(f"Feed written to {args.output}", file=sys.stderr)
    else:
        import io
        buf = io.StringIO()
        feed.write(buf, "utf-8")
        print(buf.getvalue())


if __name__ == "__main__":
    main()
