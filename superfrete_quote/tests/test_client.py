"""Calculator response parsing tests."""

from __future__ import annotations

import pytest

from superfrete_quote.client import SuperFreteError, parse_calculator_response


def test_parse_list_response_uses_custom_price() -> None:
    results = parse_calculator_response(
        [
            {
                "id": 31,
                "name": "Loggi Express",
                "price": "25.00",
                "custom_price": "22.50",
                "delivery_time": 3,
                "company": {"name": "Loggi"},
            }
        ]
    )
    assert len(results) == 1
    assert results[0].price == pytest.approx(22.50)
    assert results[0].carrier_service == "Loggi / Loggi Express"
    assert results[0].transit_days == 3
    assert results[0].service_key == "31"


def test_parse_returns_all_usable_services() -> None:
    results = parse_calculator_response(
        [
            {
                "id": 1,
                "name": "PAC",
                "price": 20.0,
                "delivery_time": 8,
                "company": {"name": "Correios"},
            },
            {
                "id": 2,
                "name": "SEDEX",
                "price": 35.0,
                "delivery_time": 3,
                "company": {"name": "Correios"},
            },
            {"id": 31, "error": "unavailable", "has_error": True},
        ]
    )
    assert [r.service_key for r in results] == ["1", "2"]
    assert results[0].price == pytest.approx(20.0)
    assert results[1].price == pytest.approx(35.0)


def test_parse_skips_errored_quote_and_keeps_next() -> None:
    results = parse_calculator_response(
        [
            {"id": 31, "error": "unavailable", "has_error": True},
            {
                "id": 31,
                "name": "Loggi",
                "price": 40.0,
                "delivery": 5,
                "company": {"name": "Loggi"},
            },
        ]
    )
    assert len(results) == 1
    assert results[0].price == pytest.approx(40.0)
    assert results[0].transit_days == 5


def test_parse_raises_when_no_usable_quote() -> None:
    with pytest.raises(SuperFreteError, match="no usable quote"):
        parse_calculator_response([{"id": 31, "error": "too heavy"}])


def test_parse_single_object_response() -> None:
    results = parse_calculator_response(
        {
            "id": 31,
            "name": "Loggi",
            "price": 19.79,
            "delivery_max": 4,
            "company": {"name": "Loggi"},
        }
    )
    assert len(results) == 1
    assert results[0].price == pytest.approx(19.79)
    assert results[0].transit_days == 4
