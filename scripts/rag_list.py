#!/usr/bin/env python3
"""rag-list — List all indexed sites in the RAG database.

Usage:
    rag-list [--format json|text] [--output file]
"""

from __future__ import annotations

import argparse
import json
import sys

from rag_common import DatabaseManager, get_logger


def main():
    parser = argparse.ArgumentParser(description="List all indexed sites in the RAG database")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    args = parser.parse_args()

    log = get_logger("rag_list")
    db = DatabaseManager()
    sites = db.list_sites()
    db.close()

    log.info("listed sites - count=%d", len(sites))

    if args.format == "json":
        data = [
            {
                "url": s["url"],
                "title": s["title"],
                "content_hash": s["content_hash"],
                "status_code": s["status_code"],
                "embed_model": s["embed_model"],
                "indexed_at": s["indexed_at"],
                "checked_at": s["checked_at"],
                "updated_count": s["updated_count"],
            }
            for s in sites
        ]
        output = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        if not sites:
            output = "No sites indexed. Use rag-index <url> to add sites."
        else:
            lines = [f"# Indexed Sites: {len(sites)}", ""]
            for s in sites:
                lines.append(f"  URL:      {s['url']}")
                lines.append(f"  Title:    {s['title'] or 'N/A'}")
                lines.append(f"  Hash:     {s['content_hash'][:16]}..." if s['content_hash'] else "  Hash:     N/A")
                lines.append(f"  Model:    {s['embed_model']}")
                lines.append(f"  Indexed:  {s['indexed_at']}")
                lines.append(f"  Checked:  {s['checked_at']}")
                lines.append(f"  Updates:  {s['updated_count']}")
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
