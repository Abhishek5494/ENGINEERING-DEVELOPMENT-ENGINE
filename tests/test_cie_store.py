"""Tests for the CIE component store (T-0401)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cie.model import Component, ComponentError, MotorSpec
from src.cie.store import ComponentStore, load_components_json


@pytest.fixture()
def store(tmp_path):
    return ComponentStore(tmp_path / "components.sqlite")


def _component(**kwargs: object) -> Component:
    return Component(id="c1", name="NEMA17", **kwargs)  # type: ignore[arg-type]


def test_save_get_roundtrip(tmp_path) -> None:
    store = ComponentStore(tmp_path / "db.sqlite3")
    component = Component(
        id="nema17",
        category="motor",
        manufacturer="Acme",
        source_urls=("https://example.invalid/p",),
        specifications={"steps": 200},
        motor=MotorSpec(rated_voltage=12.0, kv=100),
    )
    store.save(component)
    assert store.get("c1" if False else "nema17") == component
    assert store.get("missing") is None


def test_save_is_upsert(tmp_path) -> None:
    store = ComponentStore(tmp_path / "db.sqlite")
    store.save(Component(id="c1", name="first"))
    store.save(Component(id="c1", name="second"))
    rows = store.all()
    assert len(rows) == 1
    assert rows[0].name == "second"


def test_all_sorted_and_delete(tmp_path) -> None:
    store = ComponentStore(tmp_path / "db.sqlite")
    for cid in ("c3", "c1", "c2"):
        store.save(Component(id=cid))
    assert [c.id for c in store.all()] == ["c1", "c2", "c3"]
    assert store.delete("c2") is True
    assert store.delete("c2") is False
    assert [c.id for c in store.all()] == ["c1", "c3"]


def test_export_import_json_roundtrip(tmp_path) -> None:
    store = ComponentStore(tmp_path / "db.sqlite")
    original = [Component(id="a", name="A"), Component(id="b", name="B")]
    for component in original:
        store.save(component)
    out = store.export_json(tmp_path / "out.json")
    assert load_components_json(out) == original

    fresh = ComponentStore(tmp_path / "fresh.sqlite")
    assert fresh.import_json(out) == 2
    assert fresh.all() == original


def test_store_persists_between_instances(tmp_path) -> None:
    path = tmp_path / "db.sqlite"
    ComponentStore(path).save(Component(id="x", manufacturer="Acme"))
    assert ComponentStore(path).get("x").manufacturer == "Acme"  # type: ignore[union-attr]


def test_save_rejects_non_component(tmp_path) -> None:
    store = ComponentStore(tmp_path / "db.sqlite")
    with pytest.raises(ComponentError):
        store.save("not a component")  # type: ignore[arg-type]