#!/usr/bin/env python3
"""rag-index — Scrape a URL, store content in SQLite, and optionally embed chunks.

Usage:
    rag-index <url> [--only-main-content] [--timeout seconds] [--force]
              [--chunk-size N] [--chunk-overlap N]

Embeddings are generated only when /workspace/.agentispace/credentials.json
contains embed_api_key and embed_model. Otherwise only scraping and
keyword-searchable storage is performed.
"""

from __future__ import annotations

import argparse
import sys

import requests
from bs4 import BeautifulSoup
from html2text import HTML2Text

from rag_common import (
    DatabaseManager,
    EmbeddingsFactory,
    chunk_text,
    compute_content_hash,
    get_logger,
    load_credentials,
    USER_AGENT,
)


def html_to_markdown(html: str, only_main_content: bool = False) -> str:
    """Convert HTML to clean markdown."""
    h = HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0

    if only_main_content:
        soup = BeautifulSoup(html, "lxml")
        main_selectors = [
            "main", "article", "[role='main']",
            ".content", "#content", ".post-content",
            ".article-content", "main article",
        ]
        main_elem = None
        for selector in main_selectors:
            main_elem = soup.select_one(selector)
            if main_elem:
                break
        if main_elem:
            html = str(main_elem)
        else:
            for tag in soup.find_all(["nav", "header", "footer", "aside", "sidebar"]):
                tag.decompose()
            html = str(soup)

    return h.handle(html)


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""


def index_url(
    url: str,
    only_main_content: bool = False,
    timeout: int = 30,
    force: bool = False,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> dict:
    """Index a single URL: fetch, store, chunk, and optionally embed."""
    log = get_logger("rag_index")
    log.info("indexing started - url=%s", url)

    # ── Fetch ────────────────────────────────────────────────────
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error("fetch failed - url=%s error=%s", url, exc)
        return {"url": url, "success": False, "error": str(exc)}

    html = resp.text
    title = extract_title(html)
    markdown = html_to_markdown(html, only_main_content)
    content_hash = compute_content_hash(markdown)
    log.info("fetched - url=%s title=%s hash=%s", url, title[:80], content_hash[:16])

    # ── Check if already indexed and unchanged ────────────────────
    db = DatabaseManager()
    existing = db.get_site(url)
    if existing and not force and existing["content_hash"] == content_hash:
        log.info("content unchanged, skipping - url=%s", url)
        db.mark_checked(url, changed=False)
        db.close()
        return {
            "url": url,
            "success": True,
            "action": "skipped",
            "reason": "content unchanged",
            "title": title,
            "content_hash": content_hash,
        }

    # ── Credentials & embeddings ─────────────────────────────────
    creds = load_credentials()
    embed_service = EmbeddingsFactory.create(creds)
    embed_model = embed_service.provider_name if embed_service.is_available() else "none"

    if embed_service.is_available():
        log.info("embeddings enabled - provider=%s", embed_service.provider_name)
    else:
        log.info("embeddings disabled, keyword-only mode - provider=%s", embed_service.provider_name)

    # ── Store site ───────────────────────────────────────────────
    site_id = db.upsert_site(
        url=url,
        title=title,
        content_hash=content_hash,
        content=html[:200000],
        markdown=markdown,
        status_code=resp.status_code,
        embed_model=embed_model,
    )

    # ── Chunk & embed ────────────────────────────────────────────
    chunks = chunk_text(markdown, size=chunk_size, overlap=chunk_overlap)
    log.info("chunking complete - url=%s chunks=%d", url, len(chunks))

    embedded_count = 0
    if embed_service.is_available() and chunks:
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            try:
                embeddings = embed_service.embed(batch)
                for j, emb in enumerate(embeddings):
                    db.insert_chunk(site_id, i + j, batch[j], emb)
                embedded_count += len(embeddings)
                log.info(
                    "embedded batch - url=%s batch=%d/%d",
                    url, i // batch_size + 1, (len(chunks) + batch_size - 1) // batch_size,
                )
            except Exception as exc:
                log.error("embedding batch failed - url=%s error=%s", url, exc)
                for j, text in enumerate(batch):
                    db.insert_chunk(site_id, i + j, text, None)
    else:
        for idx, text in enumerate(chunks):
            db.insert_chunk(site_id, idx, text, None)

    db.commit_chunks()
    db.close()

    log.info(
        "indexing complete - url=%s chunks=%d embedded=%d",
        url, len(chunks), embedded_count,
    )

    return {
        "url": url,
        "success": True,
        "action": "indexed",
        "title": title,
        "content_hash": content_hash,
        "chunks": len(chunks),
        "embedded_chunks": embedded_count,
        "embed_model": embed_model,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scrape a URL, store in SQLite, and optionally embed chunks for RAG"
    )
    parser.add_argument("url", help="URL to index")
    parser.add_argument("--only-main-content", action="store_true",
                        help="Extract only main content, skip navigation/footer")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--force", action="store_true",
                        help="Force re-indexing even if content hash is unchanged")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size in words")
    parser.add_argument("--chunk-overlap", type=int, default=64, help="Overlap between chunks")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    args = parser.parse_args()

    result = index_url(
        url=args.url,
        only_main_content=args.only_main_content,
        timeout=args.timeout,
        force=args.force,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if args.format == "json":
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            action = result.get("action", "unknown")
            print(f"[OK] {action}: {result['url']}")
            if action == "indexed":
                print(f"  Title:   {result.get('title', 'N/A')}")
                print(f"  Chunks:  {result.get('chunks', 0)}")
                print(f"  Embedded:{result.get('embedded_chunks', 0)}")
                print(f"  Model:   {result.get('embed_model', 'none')}")
                print(f"  Hash:    {result.get('content_hash', '')[:16]}...")
            elif action == "skipped":
                print(f"  Reason:  {result.get('reason', '')}")
        else:
            print(f"[FAIL] {result['url']}: {result.get('error', 'unknown error')}",
                  file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
