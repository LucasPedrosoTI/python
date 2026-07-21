"""Insurance and output currency conversion tests."""

from __future__ import annotations

import pytest

from superfrete_quote.config import ProductConfig, QuoteConfig
from superfrete_quote.products import (
    convert_output_price,
    resolve_insurance_value_brl,
)


def _quote(**overrides: object) -> QuoteConfig:
    base = dict(
        from_postal_code="08538300",
        services="31",
        use_insurance_value=True,
        max_insurance_value_brl=3000.0,
        usd_brl_rate=5.50,
        output_currency="BRL",
    )
    base.update(overrides)
    return QuoteConfig(**base)  # type: ignore[arg-type]


def test_resolve_insurance_uses_brl_when_provided() -> None:
    product = ProductConfig(
        key="managed",
        label="Managed",
        length_cm=73,
        width_cm=50,
        height_cm=26,
        weight_kg=18.98,
        insurance_value_brl=3000.0,
    )
    assert resolve_insurance_value_brl(product, _quote()) == 3000.0


def test_resolve_insurance_caps_brl_above_max() -> None:
    product = ProductConfig(
        key="managed",
        label="Managed",
        length_cm=73,
        width_cm=50,
        height_cm=26,
        weight_kg=18.98,
        insurance_value_brl=5000.0,
    )
    assert resolve_insurance_value_brl(product, _quote()) == 3000.0


def test_resolve_insurance_converts_usd_then_caps() -> None:
    product = ProductConfig(
        key="fixed_wireless",
        label="Fixed Wireless",
        length_cm=30,
        width_cm=22,
        height_cm=18,
        weight_kg=3.10,
        insurance_value_usd=350.0,
    )
    # 350 * 5.50 = 1925.0 < 3000
    assert resolve_insurance_value_brl(product, _quote()) == pytest.approx(1925.0)


def test_resolve_insurance_caps_converted_usd_above_max() -> None:
    product = ProductConfig(
        key="fixed_wireless",
        label="Fixed Wireless",
        length_cm=30,
        width_cm=22,
        height_cm=18,
        weight_kg=3.10,
        insurance_value_usd=1000.0,
    )
    quote = _quote(usd_brl_rate=5.50, max_insurance_value_brl=3000.0)
    # 1000 * 5.50 = 5500 → capped
    assert resolve_insurance_value_brl(product, quote) == 3000.0


def test_convert_output_price_keeps_brl() -> None:
    assert convert_output_price(110.0, _quote(output_currency="BRL")) == 110.0


def test_convert_output_price_divides_by_rate_for_usd() -> None:
    quote = _quote(output_currency="USD", usd_brl_rate=5.50)
    assert convert_output_price(110.0, quote) == pytest.approx(20.0)
