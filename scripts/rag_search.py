#!/usr/bin/env python3
"""rag-search — Search the RAG index by semantic similarity or keyword matching.

Usage:
    rag-search <query> [--limit N] [--format json|text] [--threshold F]
              [--no-embeddings]

When embeddings are available (credentials.json configured), performs
cosine similarity search across chunk embeddings. Otherwise falls back
to keyword-based scoring using TF-IDF-like term matching.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter

from rag_common import (
    DatabaseManager,
    EmbeddingsFactory,
    get_logger,
    load_credentials,
)


# ─── Semantic search (cosine similarity) ──────────────────────────────


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(
    db: DatabaseManager,
    query_embedding: list[float],
    limit: int,
    threshold: float,
) -> list[dict]:
    """Search chunks by cosine similarity to the query embedding."""
    log = get_logger("rag_search.semantic")
    rows = db.get_all_chunks_with_embeddings()
    if not rows:
        log.warning("no embedded chunks found in database")
        return []

    scored: list[dict] = []
    for row in rows:
        emb = json.loads(row["embedding"])
        score = cosine_similarity(query_embedding, emb)
        if score >= threshold:
            scored.append({
                "url": row["url"],
                "title": row["title"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "score": round(score, 4),
                "method": "semantic",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    log.info("semantic search - candidates=%d returned=%d", len(scored), min(len(scored), limit))
    return scored[:limit]


# ─── Keyword search (TF-IDF-like) ─────────────────────────────────────


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def keyword_search(
    db: DatabaseManager,
    query: str,
    limit: int,
    threshold: float,
) -> list[dict]:
    """Search chunks by keyword overlap scoring."""
    log = get_logger("rag_search.keyword")
    rows = db.get_all_chunks()
    if not rows:
        log.warning("no chunks found in database")
        return []

    query_terms = set(_tokenize(query))
    if not query_terms:
        return []

    # Compute document frequencies for IDF
    all_chunks = db.get_all_chunks()
    df: Counter = Counter()
    for row in all_chunks:
        terms = set(_tokenize(row["chunk_text"]))
        for term in terms:
            df[term] += 1
    total_docs = len(all_chunks)

    scored: list[dict] = []
    for row in all_chunks:
        chunk_terms = _tokenize(row["chunk_text"])
        if not chunk_terms:
            continue
        tf = Counter(chunk_terms)
        chunk_len = len(chunk_terms)

        score = 0.0
        for term in query_terms:
            if term in tf:
                idf = math.log((total_docs + 1) / (df[term] + 1)) + 1
                score += (tf[term] / chunk_len) * idf

        # Normalise by query length
        if score > 0:
            score = score / max(1, math.sqrt(len(query_terms)))

        if score >= threshold:
            scored.append({
                "url": row["url"],
                "title": row["title"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "score": round(score, 4),
                "method": "keyword",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    log.info("keyword search - candidates=%d returned=%d", len(scored), min(len(scored), limit))
    return scored[:limit]


# ─── Main ─────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Search the RAG index (semantic or keyword)"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--threshold", "-t", type=float, default=0.01,
                        help="Minimum score threshold (default: 0.01)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    parser.add_argument("--no-embeddings", action="store_true",
                        help="Force keyword search even if embeddings are available")
    args = parser.parse_args()

    log = get_logger("rag_search")
    db = DatabaseManager()

    creds = load_credentials()
    embed_service = EmbeddingsFactory.create(creds)
    use_semantic = embed_service.is_available() and not args.no_embeddings

    results: list[dict] = []

    if use_semantic:
        log.info("using semantic search - provider=%s", embed_service.provider_name)
        try:
            query_emb = embed_service.embed([args.query])[0]
            results = semantic_search(db, query_emb, args.limit, args.threshold)
        except Exception as exc:
            log.error("semantic search failed, falling back to keyword - error=%s", exc)
            results = keyword_search(db, args.query, args.limit, args.threshold)
    else:
        log.info("using keyword search")
        results = keyword_search(db, args.query, args.limit, args.threshold)

    db.close()

    if args.format == "json":
        output = json.dumps(
            {"query": args.query, "method": results[0]["method"] if results else "none",
             "results": results},
            ensure_ascii=False, indent=2,
        )
        print(output)
    else:
        if not results:
            print(f"No results for: {args.query}", file=sys.stderr)
            sys.exit(0)

        method = results[0]["method"]
        print(f"# Search: {args.query}")
        print(f"# Method: {method} | Results: {len(results)}")
        print()
        for i, r in enumerate(results, 1):
            print(f"## {i}. [{r['score']:.4f}] {r['title']}")
            print(f"   URL:   {r['url']}")
            print(f"   Chunk: #{r['chunk_index']}")
            preview = r["chunk_text"][:300].replace("\n", " ")
            print(f"   Text:  {preview}...")
            print()


if __name__ == "__main__":
    main()
