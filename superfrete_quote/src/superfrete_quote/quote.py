"""Orchestrate destination × product SuperFrete quotes (one CSV row per service)."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TextIO

from superfrete_quote.client import QuoteResult, SuperFreteClient, SuperFreteError
from superfrete_quote.config import (
    AppConfig,
    DestinationConfig,
    ProductConfig,
    QuoteConfig,
)
from superfrete_quote.products import (
    build_calculator_payload,
    convert_output_price,
    resolve_insurance_value_brl,
)


@dataclass
class DestinationRow:
    destination: DestinationConfig
    # Successful quote → float price; failure → error message string.
    prices_by_key: dict[str, float | str] = field(default_factory=dict)
    carrier_service: str = ""
    transit_days: int | None = None
    errors: list[str] = field(default_factory=list)
    service_key: str = ""


@dataclass
class QuoteRunResult:
    rows: list[DestinationRow]
    failure_count: int


def run_quotes(
    config: AppConfig,
    client: SuperFreteClient,
    *,
    progress: TextIO | None = None,
) -> QuoteRunResult:
    progress = progress or sys.stderr
    rows: list[DestinationRow] = []
    failure_count = 0
    total = len(config.destinations) * len(config.products)
    done = 0

    for destination in config.destinations:
        # product key → list of quotes OR a call-level error string
        by_product: dict[str, list[QuoteResult] | str] = {}

        for product in config.products:
            done += 1
            progress.write(
                f"[{done}/{total}] {destination.label} — {product.key}...\n"
            )
            progress.flush()
            try:
                by_product[product.key] = _quote_one(
                    config, client, destination, product
                )
            except SuperFreteError as exc:
                error_text = str(exc)
                by_product[product.key] = error_text
                progress.write(f"  error: {error_text}\n")
                progress.flush()

        dest_rows, dest_failures = build_rows_for_destination(
            destination=destination,
            products=config.products,
            by_product=by_product,
            quote_config=config.quote,
        )
        failure_count += dest_failures
        rows.extend(dest_rows)

    return QuoteRunResult(rows=rows, failure_count=failure_count)


def build_rows_for_destination(
    *,
    destination: DestinationConfig,
    products: tuple[ProductConfig, ...],
    by_product: dict[str, list[QuoteResult] | str],
    quote_config: QuoteConfig,
) -> tuple[list[DestinationRow], int]:
    """Pivot product quotes into one row per service."""
    service_order = _ordered_service_keys(by_product, quote_config.services)
    failure_count = 0

    if not service_order:
        # Every product call failed — emit a single error row.
        row = DestinationRow(destination=destination)
        for product in products:
            value = by_product.get(product.key, "no quote")
            error_text = value if isinstance(value, str) else "no usable quote"
            row.prices_by_key[product.key] = error_text
            row.errors.append(f"{product.key}: {error_text}")
            failure_count += 1
        row.carrier_service = row.errors[0] if row.errors else "error"
        return [row], failure_count

    rows: list[DestinationRow] = []
    for service_key in service_order:
        row = DestinationRow(destination=destination, service_key=service_key)
        quotes_for_meta: dict[str, QuoteResult] = {}

        for product in products:
            value = by_product.get(product.key)
            if isinstance(value, str):
                row.prices_by_key[product.key] = value
                row.errors.append(f"{product.key}: {value}")
                failure_count += 1
                continue

            matched = _find_quote(value or [], service_key)
            if matched is None:
                msg = f"no quote for service {service_key}"
                row.prices_by_key[product.key] = msg
                row.errors.append(f"{product.key}: {msg}")
                failure_count += 1
                continue

            quotes_for_meta[product.key] = matched
            row.prices_by_key[product.key] = convert_output_price(
                matched.price, quote_config
            )

        meta = _pick_meta_quote(products, quotes_for_meta)
        if meta is not None:
            row.carrier_service = meta.carrier_service
            row.transit_days = meta.transit_days
        elif row.errors:
            row.carrier_service = row.errors[0]

        rows.append(row)

    return rows, failure_count


def _quote_one(
    config: AppConfig,
    client: SuperFreteClient,
    destination: DestinationConfig,
    product: ProductConfig,
) -> list[QuoteResult]:
    insurance = resolve_insurance_value_brl(product, config.quote)
    payload = build_calculator_payload(
        from_postal_code=config.quote.from_postal_code,
        to_postal_code=destination.postal_code,
        services=config.quote.services,
        product=product,
        insurance_value_brl=insurance,
        use_insurance_value=config.quote.use_insurance_value,
    )
    return client.calculate(payload)


def _parse_requested_service_ids(services: str) -> list[str]:
    keys: list[str] = []
    for part in services.split(","):
        stripped = part.strip()
        if stripped:
            keys.append(stripped)
    return keys


def _ordered_service_keys(
    by_product: dict[str, list[QuoteResult] | str],
    requested_services: str,
) -> list[str]:
    """Order services as requested in config, then any extras from the API."""
    seen_meta: dict[str, QuoteResult] = {}
    for value in by_product.values():
        if isinstance(value, str):
            continue
        for quote in value:
            seen_meta.setdefault(quote.service_key, quote)

    if not seen_meta:
        return []

    ordered: list[str] = []
    for requested in _parse_requested_service_ids(requested_services):
        if requested in seen_meta and requested not in ordered:
            ordered.append(requested)

    for key in seen_meta:
        if key not in ordered:
            ordered.append(key)
    return ordered


def _find_quote(quotes: list[QuoteResult], service_key: str) -> QuoteResult | None:
    for quote in quotes:
        if quote.service_key == service_key:
            return quote
    return None


def _pick_meta_quote(
    products: tuple[ProductConfig, ...],
    quotes_by_key: dict[str, QuoteResult],
) -> QuoteResult | None:
    """Prefer Managed, else first successful product for carrier/transit."""
    if "managed" in quotes_by_key:
        return quotes_by_key["managed"]
    for product in products:
        if product.key in quotes_by_key:
            return quotes_by_key[product.key]
    return None
