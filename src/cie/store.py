"""Component store: SQLite persistence + JSON import/export (T-0401).

Round-trips `src.cie.model.Component` records losslessly. SQLite is the
primary store (one row per component, keyed by id); JSON import/export
supports interchange. No network. Standard library only.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from src.cie.model import Component, ComponentError

_SCHEMA = "CREATE TABLE IF NOT EXISTS components (id TEXT PRIMARY KEY, record TEXT NOT NULL)"


class ComponentStore:
    """A SQLite-backed collection of component records."""

    def __init__(self, path: str | Path, *, create: bool = True) -> None:
        self.path = Path(path)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def save(self, component: Component) -> None:
        """Insert or replace a component by id (idempotent upsert)."""
        if not isinstance(component, Component):
            raise ComponentError("save() expects a Component")
        payload = json.dumps(component.to_dict(), sort_keys=True, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO components(id, record) VALUES(?, ?) "
                "ON CONFLICT(id) DO UPDATE SET record = excluded.record",
                (component.id, payload),
            )

    def get(self, component_id: str) -> Component | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record FROM components WHERE id = ?", (component_id,)
            ).fetchone()
        return Component.from_dict(json.loads(row["record"])) if row else None

    def all(self) -> list[Component]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record FROM components ORDER BY id"
            ).fetchall()
        return [Component.from_dict(json.loads(row["record"])) for row in rows]

    def delete(self, component_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM components WHERE id = ?", (component_id,)
            )
        return cursor.rowcount > 0

    def export_json(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps([component.to_dict() for component in self.all()], indent=2),
            encoding="utf-8",
        )
        return target

    def import_json(self, path: str | Path) -> int:
        count = 0
        for component in load_components_json(path):
            self.save(component)
            count += 1
        return count


def load_components_json(path: str | Path) -> list[Component]:
    """Load a list of component records from a JSON file."""
    raw: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ComponentError("component JSON must be a list of records")
    return [Component.from_dict(item) for item in raw]


def export_components_json(components: Iterable[Component], path: str | Path) -> Path:
    """Write an iterable of components to a JSON file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([component.to_dict() for component in components], indent=2),
        encoding="utf-8",
    )
    return target


__all__ = ["ComponentStore", "export_components_json", "load_components_json"]