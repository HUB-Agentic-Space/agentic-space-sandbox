#!/usr/bin/env python3
"""rag-remove — Remove a site and its chunks from the RAG index.

Usage:
    rag-remove <url> [--format json|text]
"""

from __future__ import annotations

import argparse
import json
import sys

from rag_common import DatabaseManager, get_logger


def main():
    parser = argparse.ArgumentParser(description="Remove a site from the RAG index")
    parser.add_argument("url", help="URL to remove from the index")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    args = parser.parse_args()

    log = get_logger("rag_remove")
    db = DatabaseManager()
    removed = db.remove_site(args.url)
    db.close()

    result = {"url": args.url, "removed": removed}

    if removed:
        log.info("site removed - url=%s", args.url)
    else:
        log.warning("site not found - url=%s", args.url)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if removed:
            print(f"[OK] Removed: {args.url}")
        else:
            print(f"[NOT FOUND] {args.url}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
