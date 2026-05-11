from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import List, Tuple


WaypointRow = Tuple[float, float, float, float, float, float, float]


def resolve_db_path(db_path: str = "") -> Path:
    if db_path:
        candidate = Path(db_path).expanduser().resolve()
        if candidate.exists():
            return candidate

    candidates = [
        Path.cwd() / "tours.db",
        Path(__file__).resolve().parents[2] / "tours.db",
        Path(__file__).resolve().parents[3] / "tours.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return Path(db_path).expanduser().resolve() if db_path else candidates[0]


def load_waypoints(db_path: str = "") -> List[WaypointRow]:
    resolved = resolve_db_path(db_path)
    if not resolved.exists():
        return []

    with sqlite3.connect(str(resolved)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tours (
                px REAL,
                py REAL,
                pz REAL,
                qx REAL,
                qy REAL,
                qz REAL,
                qw REAL
            )
            """
        )
        rows = cursor.execute("SELECT px, py, pz, qx, qy, qz, qw FROM tours").fetchall()

    waypoints: List[WaypointRow] = []
    for row in rows:
        waypoints.append(
            (
                float(row[0]),
                float(row[1]),
                float(row[2]),
                float(row[3]),
                float(row[4]),
                float(row[5]),
                float(row[6]),
            )
        )
    return waypoints
