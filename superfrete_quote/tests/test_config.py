"""Config loading and validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from superfrete_quote.config import load_config


def test_load_example_config_has_twenty_seven_destinations() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_config(
        root / "config.toml.example",
        example_path=root / "config.toml.example",
    )
    assert len(config.destinations) == 27
    assert len(config.products) == 3
    assert config.quote.services == "31"
    assert config.quote.output_currency == "BRL"


def test_reject_invalid_output_currency(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        """
[api]
base_url = "https://sandbox.superfrete.com/api/v0"
token = "t"
user_agent = "Test (a@b.com)"

[quote]
from_postal_code = "08538300"
services = "31"
use_insurance_value = true
max_insurance_value_brl = 3000.0
usd_brl_rate = 5.5
output_currency = "EUR"

[[products]]
key = "managed"
label = "Managed"
length_cm = 1
width_cm = 1
height_cm = 1
weight_kg = 1
insurance_value_brl = 100

[[destinations]]
uf = "SP"
name = "São Paulo"
postal_code = "01000000"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="output_currency"):
        load_config(path)


def test_prefer_local_config_over_example(tmp_path: Path) -> None:
    local = tmp_path / "config.toml"
    example = tmp_path / "config.toml.example"
    content = """
[api]
base_url = "https://sandbox.superfrete.com/api/v0"
token = "local-token"
user_agent = "Test (a@b.com)"

[quote]
from_postal_code = "08538300"
services = "31"
use_insurance_value = true
max_insurance_value_brl = 3000.0
usd_brl_rate = 5.5
output_currency = "USD"

[[products]]
key = "managed"
label = "Managed"
length_cm = 1
width_cm = 1
height_cm = 1
weight_kg = 1
insurance_value_brl = 100

[[destinations]]
uf = "SP"
name = "São Paulo"
postal_code = "01000000"
"""
    local.write_text(content, encoding="utf-8")
    example.write_text(content.replace("local-token", "example-token"), encoding="utf-8")
    config = load_config(local, example_path=example)
    assert config.api.token == "local-token"
    assert config.quote.output_currency == "USD"
