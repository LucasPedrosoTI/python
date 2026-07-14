"""Load TOML configuration (local config.toml, else example defaults)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config.toml"
_EXAMPLE_CONFIG_PATH = _PROJECT_ROOT / "config.toml.example"


@dataclass(frozen=True)
class OutputConfig:
    digits_only: bool = True


@dataclass(frozen=True)
class CliConfig:
    python_path: str | None = None


@dataclass(frozen=True)
class AppConfig:
    output: OutputConfig
    cli: CliConfig


def _project_root() -> Path:
    return _PROJECT_ROOT


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise TypeError(f"Expected bool, got {type(value).__name__}")


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise TypeError(f"Expected str, got {type(value).__name__}")


def _parse(data: dict[str, Any]) -> AppConfig:
    output_raw = data.get("output") or {}
    cli_raw = data.get("cli") or {}
    return AppConfig(
        output=OutputConfig(
            digits_only=_as_bool(output_raw.get("digits_only"), True),
        ),
        cli=CliConfig(
            python_path=_as_optional_str(cli_raw.get("python_path")),
        ),
    )


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        loaded = tomllib.load(handle)
    if not isinstance(loaded, dict):
        raise TypeError(f"Config root must be a table: {path}")
    return loaded


def load_config(
    config_path: Path | None = None,
    *,
    example_path: Path | None = None,
) -> AppConfig:
    """Load local config.toml if present; otherwise config.toml.example; else defaults."""
    local_path = config_path or _DEFAULT_CONFIG_PATH
    fallback_path = example_path or _EXAMPLE_CONFIG_PATH

    if local_path.is_file():
        return _parse(_load_toml(local_path))
    if fallback_path.is_file():
        return _parse(_load_toml(fallback_path))
    return AppConfig(output=OutputConfig(), cli=CliConfig())
