#!/usr/bin/env python3
"""rag-update — Check indexed sites for content changes and re-index if needed.

Usage:
    rag-update [url] [--timeout seconds] [--all] [--format json|text]

If a URL is given, checks only that site. With --all (or no arguments),
checks every indexed site. Re-indexes sites whose content hash has changed.
"""

from __future__ import annotations

import argparse
import json
import sys

import requests

from rag_common import (
    DatabaseManager,
    compute_content_hash,
    get_logger,
    load_credentials,
    USER_AGENT,
)
from rag_index import html_to_markdown, index_url


def check_site(url: str, timeout: int = 30) -> dict:
    """Check if a site's content has changed since last indexing.

    Returns a dict with url, changed (bool), old_hash, new_hash.
    Does NOT re-index — caller should call index_url() if changed.
    """
    log = get_logger("rag_update")
    db = DatabaseManager()
    site = db.get_site(url)

    if not site:
        db.close()
        return {"url": url, "changed": False, "error": "site not in index"}

    log.info("checking site - url=%s old_hash=%s", url, site["content_hash"][:16])

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error("fetch failed - url=%s error=%s", url, exc)
        db.mark_checked(url, changed=False)
        db.close()
        return {"url": url, "changed": False, "error": str(exc)}

    html = resp.text
    markdown = html_to_markdown(html)
    new_hash = compute_content_hash(markdown)
    changed = new_hash != site["content_hash"]

    db.mark_checked(url, changed=changed)
    db.close()

    log.info(
        "check complete - url=%s changed=%s old=%s new=%s",
        url, changed, site["content_hash"][:16], new_hash[:16],
    )

    return {
        "url": url,
        "changed": changed,
        "old_hash": site["content_hash"],
        "new_hash": new_hash,
        "title": site["title"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check indexed sites for content changes and re-index if needed"
    )
    parser.add_argument("url", nargs="?", default=None, help="URL to check (optional)")
    parser.add_argument("--all", action="store_true", help="Check all indexed sites")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    args = parser.parse_args()

    log = get_logger("rag_update")
    db = DatabaseManager()

    if args.url:
        sites_to_check = [db.get_site(args.url)]
        if not sites_to_check[0]:
            print(f"Site not in index: {args.url}", file=sys.stderr)
            db.close()
            sys.exit(1)
    elif args.all or not args.url:
        sites_to_check = db.list_sites()
    else:
        print("Specify a URL or use --all", file=sys.stderr)
        db.close()
        sys.exit(1)

    db.close()

    if not sites_to_check:
        print("No sites in index. Use rag-index <url> to add sites.", file=sys.stderr)
        sys.exit(0)

    results: list[dict] = []
    reindexed: list[dict] = []

    for site in sites_to_check:
        url = site["url"]
        check_result = check_site(url, timeout=args.timeout)
        results.append(check_result)

        if check_result.get("changed"):
            log.info("content changed, re-indexing - url=%s", url)
            reindex_result = index_url(url, timeout=args.timeout, force=True)
            reindexed.append(reindex_result)

    if args.format == "json":
        output = json.dumps(
            {
                "checked": len(results),
                "changed": sum(1 for r in results if r.get("changed")),
                "reindexed": len(reindexed),
                "results": results,
                "reindex_details": reindexed,
            },
            ensure_ascii=False, indent=2,
        )
        print(output)
    else:
        changed_count = sum(1 for r in results if r.get("changed"))
        print(f"# Update Check: {len(results)} sites checked, {changed_count} changed")
        print()
        for r in results:
            status = "CHANGED" if r.get("changed") else "OK"
            if r.get("error"):
                status = f"ERROR: {r['error']}"
            print(f"  [{status}] {r['url']}")
            if r.get("changed"):
                print(f"    Old hash: {r['old_hash'][:16]}...")
                print(f"    New hash: {r['new_hash'][:16]}...")
        if reindexed:
            print()
            print(f"# Re-indexed: {len(reindexed)} sites")
            for r in reindexed:
                if r.get("success"):
                    print(f"  [OK] {r['url']} — chunks={r.get('chunks', 0)}")
                else:
                    print(f"  [FAIL] {r['url']} — {r.get('error', '')}")


if __name__ == "__main__":
    main()
