#!/usr/bin/env python3
"""rag_common — Shared module for RAG indexing, search, and change detection.

Provides:
  - Structured logging helper
  - Credentials loader (/workspace/.agentispace/credentials.json)
  - Embeddings service factory (OpenAI-compatible API → AgenticSpace RAG → None)
  - SQLite database manager for sites and chunks
  - Text chunking utility
  - Content hashing for change detection
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests

# ─── Constants ────────────────────────────────────────────────────────

WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", "/workspace"))
AGENTISPACE_DIR = WORKSPACE_DIR / ".agentispace"
CREDENTIALS_FILE = AGENTISPACE_DIR / "credentials.json"
DB_PATH = AGENTISPACE_DIR / "rag_index.db"
DEFAULT_EMBED_API_BASE = "https://api.openai.com/v1"
AGENTICSPACE_RAG_URL = os.environ.get(
    "AGENTICSPACE_RAG_URL", "https://app.agenticspace.rapport.tec.br/api/rag"
)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
USER_AGENT = "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"

# ─── Logging ──────────────────────────────────────────────────────────


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes structured lines to stderr."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(name)s] %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ─── Credentials ──────────────────────────────────────────────────────


@dataclass
class Credentials:
    """Holds optional embedding configuration loaded from credentials.json."""

    embed_api_key: Optional[str] = None
    embed_model: Optional[str] = None
    embed_api_base: Optional[str] = None
    agentic_rag_url: Optional[str] = None

    @property
    def has_embed_config(self) -> bool:
        return bool(self.embed_api_key and self.embed_model)


def load_credentials() -> Credentials:
    """Load credentials from /workspace/.agentispace/credentials.json.

    Returns a Credentials object with fields populated if the file exists
    and contains the expected keys. Missing keys default to None.
    """
    if not CREDENTIALS_FILE.exists():
        return Credentials()

    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        get_logger("rag_common").warning(
            "credentials file unreadable - file=%s error=%s", CREDENTIALS_FILE, exc
        )
        return Credentials()

    return Credentials(
        embed_api_key=data.get("embed_api_key"),
        embed_model=data.get("embed_model"),
        embed_api_base=data.get("embed_api_base", DEFAULT_EMBED_API_BASE),
        agentic_rag_url=data.get("agentic_rag_url", AGENTICSPACE_RAG_URL),
    )


# ─── Embeddings Service (Factory + Strategy) ──────────────────────────


class EmbeddingsService(ABC):
    """Abstract base for embedding generation strategies."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this service can generate embeddings."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name for logging."""


class OpenAIEmbeddings(EmbeddingsService):
    """OpenAI-compatible embeddings API client."""

    def __init__(self, api_key: str, model: str, api_base: str):
        self._api_key = api_key
        self._model = model
        self._api_base = api_base.rstrip("/")
        self._log = get_logger("rag_common.openai_embed")

    def is_available(self) -> bool:
        return bool(self._api_key and self._model)

    @property
    def provider_name(self) -> str:
        return f"openai:{self._model}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._log.info("embedding batch - count=%d model=%s", len(texts), self._model)
        resp = requests.post(
            f"{self._api_base}/embeddings",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={"input": texts, "model": self._model},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]


class AgenticSpaceRAGEmbeddings(EmbeddingsService):
    """Placeholder for the future AgenticSpace RAG server.

    The endpoint is not yet implemented. This class always reports
    unavailable so the system gracefully falls back to keyword search.
    """

    def __init__(self, rag_url: str):
        self._rag_url = rag_url
        self._log = get_logger("rag_common.agentic_rag")

    def is_available(self) -> bool:
        self._log.info("checking agentic rag server - url=%s", self._rag_url)
        return False

    @property
    def provider_name(self) -> str:
        return "agenticspace_rag"

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("AgenticSpace RAG server not yet available")


class NoEmbeddings(EmbeddingsService):
    """Fallback when no embedding provider is configured."""

    def is_available(self) -> bool:
        return False

    @property
    def provider_name(self) -> str:
        return "none"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return []


class EmbeddingsFactory:
    """Factory that selects the best available embeddings service."""

    @staticmethod
    def create(credentials: Credentials) -> EmbeddingsService:
        if credentials.has_embed_config:
            return OpenAIEmbeddings(
                credentials.embed_api_key,
                credentials.embed_model,
                credentials.embed_api_base or DEFAULT_EMBED_API_BASE,
            )
        if credentials.agentic_rag_url:
            return AgenticSpaceRAGEmbeddings(credentials.agentic_rag_url)
        return NoEmbeddings()


# ─── Database Manager ─────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sites (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    url           TEXT UNIQUE NOT NULL,
    title         TEXT,
    content_hash  TEXT,
    content       TEXT,
    markdown      TEXT,
    status_code   INTEGER,
    embed_model   TEXT,
    indexed_at    TEXT,
    checked_at    TEXT,
    updated_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id       INTEGER NOT NULL,
    chunk_index   INTEGER NOT NULL,
    chunk_text    TEXT NOT NULL,
    embedding     TEXT,
    created_at    TEXT NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_site_id ON chunks(site_id);
"""


class DatabaseManager:
    """SQLite manager for the RAG index."""

    def __init__(self, db_path: Path = DB_PATH):
        self._db_path = db_path
        self._log = get_logger("rag_common.db")
        self._ensure_dir()
        self._conn: sqlite3.Connection | None = None

    def _ensure_dir(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(_SCHEMA)
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._log.info("database initialized - path=%s", self._db_path)
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Site operations ───────────────────────────────────────────

    def upsert_site(
        self,
        url: str,
        title: str,
        content_hash: str,
        content: str,
        markdown: str,
        status_code: int,
        embed_model: str,
    ) -> int:
        now = _utc_now()
        cur = self.conn.execute(
            "SELECT id, content_hash FROM sites WHERE url = ?", (url,)
        )
        row = cur.fetchone()
        if row:
            updated_count = 0
            if row["content_hash"] != content_hash:
                updated_count = 1
            self.conn.execute(
                """UPDATE sites
                   SET title=?, content_hash=?, content=?, markdown=?,
                       status_code=?, embed_model=?, indexed_at=?, updated_count=updated_count+?
                   WHERE id=?""",
                (title, content_hash, content, markdown, status_code,
                 embed_model, now, updated_count, row["id"]),
            )
            self._delete_chunks(row["id"])
            self.conn.commit()
            self._log.info(
                "site updated - url=%s site_id=%d changed=%s",
                url, row["id"], updated_count == 1,
            )
            return row["id"]
        cur = self.conn.execute(
            """INSERT INTO sites
               (url, title, content_hash, content, markdown, status_code,
                embed_model, indexed_at, checked_at, updated_count)
               VALUES (?,?,?,?,?,?,?,?,?,0)""",
            (url, title, content_hash, content, markdown, status_code,
             embed_model, now, now),
        )
        self.conn.commit()
        site_id = cur.lastrowid
        self._log.info("site inserted - url=%s site_id=%d", url, site_id)
        return site_id

    def mark_checked(self, url: str, changed: bool) -> None:
        self.conn.execute(
            "UPDATE sites SET checked_at=? WHERE url=?",
            (_utc_now(), url),
        )
        if changed:
            self.conn.execute(
                "UPDATE sites SET updated_count = updated_count + 1 WHERE url=?",
                (url,),
            )
        self.conn.commit()

    def get_site(self, url: str) -> Optional[sqlite3.Row]:
        cur = self.conn.execute("SELECT * FROM sites WHERE url = ?", (url,))
        return cur.fetchone()

    def list_sites(self) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM sites ORDER BY indexed_at DESC"
        )
        return cur.fetchall()

    def remove_site(self, url: str) -> bool:
        site = self.get_site(url)
        if not site:
            return False
        self._delete_chunks(site["id"])
        self.conn.execute("DELETE FROM sites WHERE id = ?", (site["id"],))
        self.conn.commit()
        self._log.info("site removed - url=%s", url)
        return True

    # ── Chunk operations ──────────────────────────────────────────

    def _delete_chunks(self, site_id: int) -> None:
        self.conn.execute("DELETE FROM chunks WHERE site_id = ?", (site_id,))

    def insert_chunk(
        self,
        site_id: int,
        chunk_index: int,
        chunk_text: str,
        embedding: Optional[list[float]],
    ) -> None:
        emb_json = json.dumps(embedding) if embedding else None
        self.conn.execute(
            """INSERT INTO chunks (site_id, chunk_index, chunk_text, embedding, created_at)
               VALUES (?,?,?,?,?)""",
            (site_id, chunk_index, chunk_text, emb_json, _utc_now()),
        )

    def commit_chunks(self) -> None:
        self.conn.commit()

    def get_all_chunks_with_embeddings(self) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT c.*, s.url, s.title FROM chunks c "
            "JOIN sites s ON c.site_id = s.id "
            "WHERE c.embedding IS NOT NULL"
        )
        return cur.fetchall()

    def get_all_chunks(self) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT c.*, s.url, s.title FROM chunks c "
            "JOIN sites s ON c.site_id = s.id"
        )
        return cur.fetchall()

    def get_stats(self) -> dict[str, Any]:
        sites_count = self.conn.execute("SELECT COUNT(*) FROM sites").fetchone()[0]
        chunks_count = self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        embedded_count = self.conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"
        ).fetchone()[0]
        return {
            "sites": sites_count,
            "chunks": chunks_count,
            "embedded_chunks": embedded_count,
            "db_path": str(self._db_path),
        }


# ─── Text Chunking ────────────────────────────────────────────────────


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    if len(words) <= size:
        return [text.strip()] if text.strip() else []
    chunks: list[str] = []
    step = size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk.strip():
            chunks.append(chunk.strip())
        if i + size >= len(words):
            break
    return chunks


# ─── Content Hashing ──────────────────────────────────────────────────


def compute_content_hash(markdown: str) -> str:
    """Compute SHA-256 of normalised markdown for change detection."""
    normalised = re.sub(r"\s+", " ", markdown).strip()
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


# ─── Helpers ──────────────────────────────────────────────────────────


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_url(url: str, timeout: int = 30) -> tuple[int, str, str]:
    """Fetch a URL and return (status_code, html, text_content)."""
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.status_code, resp.text, resp.text
