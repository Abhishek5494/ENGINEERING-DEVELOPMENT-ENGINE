"""Tests for the shared configuration module (T-0202)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core import config
from src.core.config import (
    COMPONENTS_DIR,
    CONFIG_DIR,
    MANIFEST_PATH,
    MANIFEST_SCHEMA_PATH,
    REPO_ROOT,
    ConfigError,
    load_config,
    load_json,
    load_yaml,
    resolve_path,
    yaml_available,
)

EXPECTED_DIR_KEYS = {
    "config",
    "cad",
    "electronics",
    "simulations",
    "models",
    "data",
    "components",
    "docs",
    "projects",
    "scripts",
    "decisions",
    "tests",
}


def test_repo_root_is_project_root() -> None:
    assert (REPO_ROOT / "MASTER.md").is_file()
    assert (REPO_ROOT / "src").is_dir()
    assert (REPO_ROOT / "tests").is_dir()


def test_repo_root_independent_of_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    assert config.REPO_ROOT == REPO_ROOT
    assert (config.REPO_ROOT / "MASTER.md").is_file()


def test_canonical_directories() -> None:
    assert set(config.DIRECTORIES) == EXPECTED_DIR_KEYS
    for name, path in config.DIRECTORIES.items():
        assert path.parent == REPO_ROOT, f"{name} not directly under repo root"
    assert CONFIG_DIR == REPO_ROOT / "config"
    assert COMPONENTS_DIR == REPO_ROOT / "components"


def test_config_paths_point_at_real_files() -> None:
    assert MANIFEST_PATH == CONFIG_DIR / "tool-manifest.json"
    assert MANIFEST_SCHEMA_PATH == CONFIG_DIR / "tool-manifest.schema.json"
    assert MANIFEST_PATH.is_file()
    assert MANIFEST_SCHEMA_PATH.is_file()


def test_resolve_path_relative_and_absolute(tmp_path: Path) -> None:
    assert resolve_path("config") == REPO_ROOT / "config"
    assert resolve_path(REPO_ROOT / "config") == REPO_ROOT / "config"
    assert resolve_path(tmp_path).is_absolute()


def test_load_json_reads_object(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text(json.dumps({"x": 1, "y": {"z": 2}}), encoding="utf-8")
    assert load_json(target) == {"x": 1, "y": {"z": 2}}


def test_load_json_absolute_string_path(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text(json.dumps({"x": 1}), encoding="utf-8")
    assert load_json(str(target)) == {"x": 1}


def test_load_json_deep_merge_defaults(tmp_path: Path) -> None:
    defaults = {"a": {"b": 1, "c": 2}, "keep": 0}
    target = tmp_path / "data.json"
    target.write_text(json.dumps({"a": {"c": 3}}), encoding="utf-8")
    result = load_json(target, defaults=defaults)
    assert result == {"a": {"b": 1, "c": 3}, "keep": 0}


def test_load_json_missing_without_defaults_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_json(tmp_path / "nope.json")


def test_load_json_missing_with_defaults_returns_copy(tmp_path: Path) -> None:
    defaults = {"a": {"b": 1}}
    result = load_json(tmp_path / "nope.json", defaults=defaults)
    assert result == defaults
    assert result is not defaults
    assert result["a"] is not defaults["a"]
    result["a"]["b"] = 99
    assert defaults["a"]["b"] == 1


def test_load_json_invalid_raises(tmp_path: Path) -> None:
    target = tmp_path / "bad.json"
    target.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_json(target)


def test_load_json_non_object_root_raises(tmp_path: Path) -> None:
    target = tmp_path / "list.json"
    target.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_json(target)


def test_load_config_relative_name_uses_default_dir() -> None:
    data = load_config("tool-manifest.json")
    assert "tools" in data


def test_load_config_directory_override(tmp_path: Path) -> None:
    (tmp_path / "custom.json").write_text(json.dumps({"k": 1}), encoding="utf-8")
    assert load_config("custom.json", directory=tmp_path) == {"k": 1}


def test_load_config_absolute_path(tmp_path: Path) -> None:
    target = tmp_path / "abs.json"
    target.write_text(json.dumps({"k": 2}), encoding="utf-8")
    assert load_config(str(target)) == {"k": 2}


def test_load_config_unsupported_extension(tmp_path: Path) -> None:
    target = tmp_path / "thing.toml"
    target.write_text("k = 1", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(str(target))


def test_yaml_behaviour_is_honest(tmp_path: Path) -> None:
    target = tmp_path / "c.yaml"
    target.write_text("a:\n  b: 1\n", encoding="utf-8")
    if yaml_available():
        result = load_yaml(target, defaults={"a": {"c": 2}})
        assert result == {"a": {"b": 1, "c": 2}}
    else:
        with pytest.raises(ConfigError):
            load_yaml(target)


def test_yaml_load_config_extension_routing(tmp_path: Path) -> None:
    target = tmp_path / "c.yml"
    target.write_text("a: 1\n", encoding="utf-8")
    if yaml_available():
        assert load_config(str(target)) == {"a": 1}
    else:
        with pytest.raises(ConfigError):
            load_config(str(target))


def test_existing_modules_use_shared_root() -> None:
    from src.core import manifest as manifest_mod
    from src.pem import report as report_mod

    assert report_mod.REPO_ROOT == REPO_ROOT
    assert manifest_mod.DEFAULT_MANIFEST_PATH == MANIFEST_PATH
    assert manifest_mod.DEFAULT_SCHEMA_PATH == MANIFEST_SCHEMA_PATH