from __future__ import annotations

import datetime as _dt
import math
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


def default_knowledge_db_path() -> Path:
    return Path.home() / ".local" / "share" / "turtlebot_llm_control" / "knowledge.db"


def resolve_knowledge_db_path(db_path: str = "") -> Path:
    if db_path:
        candidate = Path(db_path).expanduser()
        if candidate.suffix == "":
            candidate = candidate / "knowledge.db"
        return candidate.resolve()
    return default_knowledge_db_path().resolve()


@dataclass
class KnowledgeEntry:
    key: str
    title: str
    kind: str = "page"
    location_key: str = ""
    x: Optional[float] = None
    y: Optional[float] = None
    yaw: Optional[float] = None
    tags: str = ""
    # What the robot says out loud when it arrives at this waypoint.
    # Leave blank to auto-generate from the first paragraph of content.
    arrival_speech: str = ""
    content: str = ""
    updated_at: str = field(default_factory=lambda: _dt.datetime.utcnow().isoformat())

    @classmethod
    def from_row(cls, row) -> "KnowledgeEntry":
        return cls(
            key=row["key"],
            title=row["title"],
            kind=row["kind"],
            location_key=row["location_key"] or "",
            x=float(row["x"]) if row["x"] is not None else None,
            y=float(row["y"]) if row["y"] is not None else None,
            yaw=float(row["yaw"]) if row["yaw"] is not None else None,
            tags=row["tags"] or "",
            arrival_speech=row["arrival_speech"] or "",
            content=row["content"] or "",
            updated_at=row["updated_at"] or "",
        )

    def to_record(self) -> dict:
        return asdict(self)


@dataclass
class KnowledgeHit:
    entry: KnowledgeEntry
    chunk: str
    score: float


class KnowledgeStore:
    def __init__(self, db_path: str = "") -> None:
        self.db_path = resolve_knowledge_db_path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    key          TEXT PRIMARY KEY,
                    title        TEXT NOT NULL,
                    kind         TEXT NOT NULL,
                    location_key TEXT,
                    x            REAL,
                    y            REAL,
                    yaw          REAL,
                    tags         TEXT,
                    arrival_speech TEXT DEFAULT '',
                    content      TEXT,
                    updated_at   TEXT NOT NULL
                )
                """
            )
            # Safe migration: add arrival_speech column to older databases.
            existing = {row[1] for row in conn.execute("PRAGMA table_info(knowledge_entries)")}
            if "arrival_speech" not in existing:
                conn.execute(
                    "ALTER TABLE knowledge_entries ADD COLUMN arrival_speech TEXT DEFAULT ''"
                )
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    _SELECT = (
        "SELECT key, title, kind, location_key, x, y, yaw, tags, "
        "arrival_speech, content, updated_at FROM knowledge_entries"
    )

    def list_entries(self) -> List[KnowledgeEntry]:
        with self.connect() as conn:
            rows = conn.execute(self._SELECT + " ORDER BY updated_at DESC").fetchall()
        return [KnowledgeEntry.from_row(r) for r in rows]

    def get_entry(self, key: str) -> Optional[KnowledgeEntry]:
        with self.connect() as conn:
            row = conn.execute(self._SELECT + " WHERE key = ?", (key,)).fetchone()
        return KnowledgeEntry.from_row(row) if row else None

    def upsert_entry(self, entry: KnowledgeEntry) -> None:
        entry.updated_at = _dt.datetime.utcnow().isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO knowledge_entries
                    (key, title, kind, location_key, x, y, yaw, tags,
                     arrival_speech, content, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    title          = excluded.title,
                    kind           = excluded.kind,
                    location_key   = excluded.location_key,
                    x              = excluded.x,
                    y              = excluded.y,
                    yaw            = excluded.yaw,
                    tags           = excluded.tags,
                    arrival_speech = excluded.arrival_speech,
                    content        = excluded.content,
                    updated_at     = excluded.updated_at
                """,
                (
                    entry.key,
                    entry.title,
                    entry.kind,
                    entry.location_key,
                    entry.x,
                    entry.y,
                    entry.yaw,
                    entry.tags,
                    entry.arrival_speech,
                    entry.content,
                    entry.updated_at,
                ),
            )
            conn.commit()

    def delete_entry(self, key: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM knowledge_entries WHERE key = ?", (key,))
            conn.commit()

    # ------------------------------------------------------------------
    # Spatial helpers
    # ------------------------------------------------------------------

    def resolve_position(
        self, entry: KnowledgeEntry
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        if entry.x is not None and entry.y is not None:
            return entry.x, entry.y, entry.yaw
        if entry.location_key:
            ref = self.get_entry(entry.location_key)
            if ref is not None and ref.x is not None and ref.y is not None:
                return ref.x, ref.y, ref.yaw
        return None, None, None

    def get_nearest_entry(
        self,
        x: float,
        y: float,
        kind: str = "",
        radius: float = 2.0,
    ) -> Optional[KnowledgeEntry]:
        """Return the closest entry to (x, y) within *radius* metres.

        If *kind* is given only entries of that kind are considered.
        Returns None when nothing is within range.
        """
        best: Optional[KnowledgeEntry] = None
        best_dist = float("inf")
        for entry in self.list_entries():
            ex, ey, _ = self.resolve_position(entry)
            if ex is None or ey is None:
                continue
            if kind and entry.kind != kind:
                continue
            dist = math.hypot(x - ex, y - ey)
            if dist < radius and dist < best_dist:
                best_dist = dist
                best = entry
        return best

    # ------------------------------------------------------------------
    # Search / RAG helpers
    # ------------------------------------------------------------------

    def search(self, query: str, limit: int = 5) -> List[KnowledgeHit]:
        tokens = self._tokenize(query)
        if not tokens:
            return []
        hits: List[KnowledgeHit] = []
        for entry in self.list_entries():
            for chunk in self._chunk_entry(entry):
                score = self._score_text(entry, chunk, tokens)
                if score > 0:
                    hits.append(KnowledgeHit(entry=entry, chunk=chunk, score=score))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def build_context(self, query: str, limit: int = 3, max_chars: int = 2400) -> str:
        hits = self.search(query, limit=limit)
        if not hits:
            return ""
        sections: List[str] = []
        total = 0
        for i, hit in enumerate(hits, 1):
            e = hit.entry
            ex, ey, eyaw = self.resolve_position(e)
            coords = ""
            if ex is not None and ey is not None:
                coords = "coords=(%.3f, %.3f" % (ex, ey)
                if eyaw is not None:
                    coords += ", yaw=%.3f" % eyaw
                coords += ")"
            summary = hit.chunk.strip()
            if len(summary) > 700:
                summary = summary[:700].rstrip() + "..."
            parts = ["Source %d" % i, "Key: %s" % e.key, "Title: %s" % e.title, "Kind: %s" % e.kind]
            if e.location_key:
                parts.append("Location key: %s" % e.location_key)
            if coords:
                parts.append(coords)
            if e.tags:
                parts.append("Tags: %s" % e.tags)
            parts.append("Content: %s" % summary)
            block = "\n".join(parts)
            if total + len(block) > max_chars:
                break
            sections.append(block)
            total += len(block)
        return "\n\n".join(sections)

    def summarize_hits(self, query: str, limit: int = 3) -> str:
        hits = self.search(query, limit=limit)
        if not hits:
            return ""
        lines: List[str] = []
        for hit in hits:
            e = hit.entry
            ex, ey, _ = self.resolve_position(e)
            loc = e.location_key or ""
            if ex is not None and ey is not None:
                loc = "at %.2f, %.2f" % (ex, ey)
            snippet = hit.chunk.strip().replace("\n", " ")
            if len(snippet) > 220:
                snippet = snippet[:220].rstrip() + "..."
            lines.append("%s (%s): %s" % (e.title, loc or e.kind, snippet))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _chunk_entry(self, entry: KnowledgeEntry) -> List[str]:
        if not entry.content.strip():
            return [entry.title]
        raw = re.split(r"\n\s*\n", entry.content.strip())
        chunks = [c.strip() for c in raw if c.strip()]
        return chunks or [entry.content.strip()]

    def _score_text(
        self, entry: KnowledgeEntry, chunk: str, query_tokens: List[str]
    ) -> float:
        title_t = set(self._tokenize(entry.title))
        tag_t = set(self._tokenize(entry.tags))
        key_t = set(self._tokenize(entry.key))
        loc_t = set(self._tokenize(entry.location_key))
        chunk_t = set(self._tokenize(chunk))
        score = 0.0
        for tok in query_tokens:
            if tok in title_t:
                score += 4.0
            if tok in tag_t:
                score += 3.0
            if tok in key_t:
                score += 4.0
            if tok in loc_t:
                score += 3.0
            if tok in chunk_t:
                score += 1.0
        if entry.location_key and entry.location_key in query_tokens:
            score += 5.0
        return score

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-z0-9_]+", text.lower())
