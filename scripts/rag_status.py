#!/usr/bin/env python3
"""rag-status — Show statistics and health of the RAG index.

Usage:
    rag-status [--format json|text]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rag_common import (
    AGENTISPACE_DIR,
    CREDENTIALS_FILE,
    DB_PATH,
    DatabaseManager,
    EmbeddingsFactory,
    get_logger,
    load_credentials,
)


def main():
    parser = argparse.ArgumentParser(description="Show RAG index statistics and health")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    args = parser.parse_args()

    log = get_logger("rag_status")

    db = DatabaseManager()
    stats = db.get_stats()
    db.close()

    creds = load_credentials()
    embed_service = EmbeddingsFactory.create(creds)

    status = {
        "db_path": stats["db_path"],
        "db_exists": Path(stats["db_path"]).exists(),
        "credentials_file": str(CREDENTIALS_FILE),
        "credentials_found": CREDENTIALS_FILE.exists(),
        "embeddings_available": embed_service.is_available(),
        "embed_provider": embed_service.provider_name,
        "embed_model": creds.embed_model if creds.has_embed_config else None,
        "sites": stats["sites"],
        "chunks": stats["chunks"],
        "embedded_chunks": stats["embedded_chunks"],
        "agentispace_dir": str(AGENTISPACE_DIR),
    }

    log.info(
        "status - sites=%d chunks=%d embedded=%d embeddings=%s",
        status["sites"], status["chunks"], status["embedded_chunks"],
        status["embeddings_available"],
    )

    if args.format == "json":
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print("# RAG Index Status")
        print()
        print(f"  Database:          {status['db_path']}")
        print(f"  DB exists:         {'yes' if status['db_exists'] else 'no'}")
        print(f"  Credentials:       {status['credentials_file']}")
        print(f"  Credentials found: {'yes' if status['credentials_found'] else 'no'}")
        print(f"  Embeddings:        {'enabled' if status['embeddings_available'] else 'disabled (keyword-only)'}")
        print(f"  Embed provider:    {status['embed_provider']}")
        if status["embed_model"]:
            print(f"  Embed model:       {status['embed_model']}")
        print()
        print(f"  Sites:             {status['sites']}")
        print(f"  Chunks:            {status['chunks']}")
        print(f"  Embedded chunks:   {status['embedded_chunks']}")
        if status["chunks"] > 0:
            ratio = status["embedded_chunks"] / status["chunks"] * 100
            print(f"  Embed coverage:    {ratio:.1f}%")


if __name__ == "__main__":
    main()
