"""Quote orchestration — one row per service."""

from __future__ import annotations

import pytest

from superfrete_quote.client import QuoteResult
from superfrete_quote.config import DestinationConfig, ProductConfig, QuoteConfig
from superfrete_quote.quote import (
    _ordered_service_keys,
    _pick_meta_quote,
    build_rows_for_destination,
)


PRODUCTS = (
    ProductConfig(
        key="managed",
        label="Managed",
        length_cm=1,
        width_cm=1,
        height_cm=1,
        weight_kg=1,
        insurance_value_brl=100,
    ),
    ProductConfig(
        key="light",
        label="Light",
        length_cm=1,
        width_cm=1,
        height_cm=1,
        weight_kg=1,
        insurance_value_brl=100,
    ),
)

DEST = DestinationConfig(uf="SP", name="São Paulo", postal_code="01001000")

QUOTE_CFG = QuoteConfig(
    from_postal_code="08538300",
    services="1,31",
    use_insurance_value=True,
    max_insurance_value_brl=3000.0,
    usd_brl_rate=5.5,
    output_currency="BRL",
)


def test_pick_meta_prefers_managed() -> None:
    managed = QuoteResult(price=10, carrier_service="Loggi / A", transit_days=2)
    light = QuoteResult(price=8, carrier_service="Loggi / B", transit_days=4)
    picked = _pick_meta_quote(PRODUCTS, {"managed": managed, "light": light})
    assert picked is managed


def test_pick_meta_falls_back_to_first_success() -> None:
    light = QuoteResult(price=8, carrier_service="Loggi / B", transit_days=4)
    picked = _pick_meta_quote(PRODUCTS, {"light": light})
    assert picked is light


def test_pick_meta_returns_none_when_empty() -> None:
    assert _pick_meta_quote(PRODUCTS, {}) is None


def test_ordered_service_keys_follows_config_order() -> None:
    by_product = {
        "managed": [
            QuoteResult(
                price=10,
                carrier_service="Loggi / L",
                transit_days=2,
                service_id=31,
            ),
            QuoteResult(
                price=8,
                carrier_service="Correios / PAC",
                transit_days=8,
                service_id=1,
            ),
        ]
    }
    assert _ordered_service_keys(by_product, "1,31") == ["1", "31"]


def test_build_rows_emits_one_row_per_service() -> None:
    by_product = {
        "managed": [
            QuoteResult(
                price=20.0,
                carrier_service="Correios / PAC",
                transit_days=8,
                service_id=1,
            ),
            QuoteResult(
                price=40.0,
                carrier_service="Loggi / Express",
                transit_days=2,
                service_id=31,
            ),
        ],
        "light": [
            QuoteResult(
                price=15.0,
                carrier_service="Correios / PAC",
                transit_days=8,
                service_id=1,
            ),
            QuoteResult(
                price=30.0,
                carrier_service="Loggi / Express",
                transit_days=2,
                service_id=31,
            ),
        ],
    }
    rows, failures = build_rows_for_destination(
        destination=DEST,
        products=PRODUCTS,
        by_product=by_product,
        quote_config=QUOTE_CFG,
    )
    assert failures == 0
    assert len(rows) == 2
    assert rows[0].service_key == "1"
    assert rows[0].carrier_service == "Correios / PAC"
    assert rows[0].prices_by_key["managed"] == pytest.approx(20.0)
    assert rows[0].prices_by_key["light"] == pytest.approx(15.0)
    assert rows[1].service_key == "31"
    assert rows[1].carrier_service == "Loggi / Express"
    assert rows[1].prices_by_key["managed"] == pytest.approx(40.0)


def test_build_rows_writes_error_when_service_missing_for_product() -> None:
    by_product = {
        "managed": [
            QuoteResult(
                price=40.0,
                carrier_service="Loggi / Express",
                transit_days=2,
                service_id=31,
            ),
        ],
        "light": [
            QuoteResult(
                price=15.0,
                carrier_service="Correios / PAC",
                transit_days=8,
                service_id=1,
            ),
        ],
    }
    rows, failures = build_rows_for_destination(
        destination=DEST,
        products=PRODUCTS,
        by_product=by_product,
        quote_config=QUOTE_CFG,
    )
    assert len(rows) == 2
    assert failures >= 1
    pac_row = next(r for r in rows if r.service_key == "1")
    assert pac_row.prices_by_key["managed"] == "no quote for service 1"
