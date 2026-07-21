"""CSV export for freight quote table."""

from __future__ import annotations

import csv
from pathlib import Path

from superfrete_quote.config import ProductConfig
from superfrete_quote.quote import DestinationRow

CARRIER_COLUMN = "Carrier / Service"
TRANSIT_COLUMN = "Transit Time (days)"
DESTINATION_COLUMN = "Destination"


def csv_headers(products: tuple[ProductConfig, ...]) -> list[str]:
    return [
        DESTINATION_COLUMN,
        *[product.label for product in products],
        CARRIER_COLUMN,
        TRANSIT_COLUMN,
    ]


def format_cell(value: float | str | None) -> str:
    """Format a price float, pass through error strings, empty if missing."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return f"{value:.2f}"


def write_quotes_csv(
    path: Path,
    rows: list[DestinationRow],
    products: tuple[ProductConfig, ...],
) -> None:
    headers = csv_headers(products)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            record: dict[str, str] = {
                DESTINATION_COLUMN: row.destination.label,
                CARRIER_COLUMN: row.carrier_service,
                TRANSIT_COLUMN: (
                    "" if row.transit_days is None else str(row.transit_days)
                ),
            }
            for product in products:
                record[product.label] = format_cell(
                    row.prices_by_key.get(product.key)
                )
            writer.writerow(record)
