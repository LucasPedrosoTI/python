"""CSV export tests."""

from __future__ import annotations

from pathlib import Path

from superfrete_quote.config import DestinationConfig, ProductConfig
from superfrete_quote.csv_export import csv_headers, format_cell, write_quotes_csv
from superfrete_quote.quote import DestinationRow


PRODUCTS = (
    ProductConfig(
        key="managed",
        label="Managed  (41.84 lb / 18.98 kg)",
        length_cm=73,
        width_cm=50,
        height_cm=26,
        weight_kg=18.98,
        insurance_value_brl=3000.0,
    ),
    ProductConfig(
        key="light",
        label="Light  (35.41 lb / 16.06 kg)",
        length_cm=73,
        width_cm=50,
        height_cm=22,
        weight_kg=16.06,
        insurance_value_brl=3000.0,
    ),
    ProductConfig(
        key="fixed_wireless",
        label="Fixed Wireless  (6.83 lb / 3.10 kg)",
        length_cm=30,
        width_cm=22,
        height_cm=18,
        weight_kg=3.10,
        insurance_value_usd=350.0,
    ),
)


def test_csv_headers_match_required_columns() -> None:
    assert csv_headers(PRODUCTS) == [
        "Destination",
        "Managed  (41.84 lb / 18.98 kg)",
        "Light  (35.41 lb / 16.06 kg)",
        "Fixed Wireless  (6.83 lb / 3.10 kg)",
        "Carrier / Service",
        "Transit Time (days)",
    ]


def test_format_cell_empty_when_missing() -> None:
    assert format_cell(None) == ""


def test_format_cell_two_decimals() -> None:
    assert format_cell(12.345) == "12.35"


def test_format_cell_passes_through_error_string() -> None:
    assert format_cell("HTTP 400 from SuperFrete: too heavy") == (
        "HTTP 400 from SuperFrete: too heavy"
    )


def test_write_quotes_csv_row_content(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    row = DestinationRow(
        destination=DestinationConfig(
            uf="SP", name="São Paulo", postal_code="01000000"
        ),
        prices_by_key={
            "managed": 41.84,
            "light": 35.41,
            "fixed_wireless": 6.83,
        },
        carrier_service="Loggi / Express",
        transit_days=3,
    )
    write_quotes_csv(out, [row], PRODUCTS)
    text = out.read_text(encoding="utf-8")
    assert "Destination,Managed  (41.84 lb / 18.98 kg)" in text
    assert "São Paulo (SP),41.84,35.41,6.83,Loggi / Express,3" in text


def test_write_quotes_csv_writes_error_in_price_cell(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    row = DestinationRow(
        destination=DestinationConfig(
            uf="AM", name="Manaus", postal_code="69000000"
        ),
        prices_by_key={
            "managed": "no usable quote in response: unavailable",
            "light": 20.0,
            "fixed_wireless": 5.0,
        },
        carrier_service="Loggi / Express",
        transit_days=5,
        errors=["managed: no usable quote in response: unavailable"],
    )
    write_quotes_csv(out, [row], PRODUCTS)
    text = out.read_text(encoding="utf-8")
    assert "no usable quote in response: unavailable" in text
    assert "20.00" in text
