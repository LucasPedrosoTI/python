"""Insurance resolution and calculator package payloads."""

from __future__ import annotations

from typing import Any

from superfrete_quote.config import ProductConfig, QuoteConfig


def resolve_insurance_value_brl(
    product: ProductConfig,
    quote: QuoteConfig,
) -> float:
    """Return insurance value in BRL, capped at max_insurance_value_brl."""
    if product.insurance_value_usd is not None:
        raw = product.insurance_value_usd * quote.usd_brl_rate
    elif product.insurance_value_brl is not None:
        raw = product.insurance_value_brl
    else:
        raise ValueError(f"product {product.key!r} has no insurance value")
    return min(raw, quote.max_insurance_value_brl)


def convert_output_price(price_brl: float, quote: QuoteConfig) -> float:
    """Convert API BRL price to the configured output currency."""
    if quote.output_currency == "BRL":
        return price_brl
    return price_brl / quote.usd_brl_rate


def build_calculator_payload(
    *,
    from_postal_code: str,
    to_postal_code: str,
    services: str,
    product: ProductConfig,
    insurance_value_brl: float,
    use_insurance_value: bool,
) -> dict[str, Any]:
    return {
        "from": {"postal_code": from_postal_code},
        "to": {"postal_code": to_postal_code},
        "services": services,
        "options": {
            "own_hand": False,
            "receipt": False,
            "insurance_value": insurance_value_brl,
            "use_insurance_value": use_insurance_value,
        },
        "package": {
            "length": product.length_cm,
            "width": product.width_cm,
            "height": product.height_cm,
            "weight": product.weight_kg,
        },
    }
