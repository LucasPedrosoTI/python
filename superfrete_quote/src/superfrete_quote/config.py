"""Load TOML configuration (local config.toml, else example)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config.toml"
_EXAMPLE_CONFIG_PATH = _PROJECT_ROOT / "config.toml.example"

OutputCurrency = Literal["BRL", "USD"]


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    token: str
    user_agent: str


@dataclass(frozen=True)
class QuoteConfig:
    from_postal_code: str
    services: str
    use_insurance_value: bool
    max_insurance_value_brl: float
    usd_brl_rate: float
    output_currency: OutputCurrency


@dataclass(frozen=True)
class ProductConfig:
    key: str
    label: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_kg: float
    insurance_value_brl: float | None = None
    insurance_value_usd: float | None = None


@dataclass(frozen=True)
class DestinationConfig:
    uf: str
    name: str
    postal_code: str

    @property
    def label(self) -> str:
        return f"{self.name} ({self.uf})"


@dataclass(frozen=True)
class AppConfig:
    api: ApiConfig
    quote: QuoteConfig
    products: tuple[ProductConfig, ...]
    destinations: tuple[DestinationConfig, ...]


def _as_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _as_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be bool, got {type(value).__name__}")
    return value


def _as_float(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a number, got {type(value).__name__}")
    return float(value)


def _as_optional_float(value: Any, field: str) -> float | None:
    if value is None:
        return None
    return _as_float(value, field)


def _parse_output_currency(value: Any) -> OutputCurrency:
    if not isinstance(value, str):
        raise TypeError(
            f"output_currency must be str, got {type(value).__name__}"
        )
    normalized = value.strip().upper()
    if normalized not in ("BRL", "USD"):
        raise ValueError('output_currency must be "BRL" or "USD"')
    return normalized  # type: ignore[return-value]


def _parse_product(raw: dict[str, Any]) -> ProductConfig:
    key = _as_str(raw.get("key"), "products.key")
    insurance_brl = _as_optional_float(
        raw.get("insurance_value_brl"), "products.insurance_value_brl"
    )
    insurance_usd = _as_optional_float(
        raw.get("insurance_value_usd"), "products.insurance_value_usd"
    )
    if insurance_brl is None and insurance_usd is None:
        raise ValueError(
            f"product {key!r} needs insurance_value_brl or insurance_value_usd"
        )
    return ProductConfig(
        key=key,
        label=_as_str(raw.get("label"), "products.label"),
        length_cm=_as_float(raw.get("length_cm"), "products.length_cm"),
        width_cm=_as_float(raw.get("width_cm"), "products.width_cm"),
        height_cm=_as_float(raw.get("height_cm"), "products.height_cm"),
        weight_kg=_as_float(raw.get("weight_kg"), "products.weight_kg"),
        insurance_value_brl=insurance_brl,
        insurance_value_usd=insurance_usd,
    )


def _parse_destination(raw: dict[str, Any]) -> DestinationConfig:
    return DestinationConfig(
        uf=_as_str(raw.get("uf"), "destinations.uf").upper(),
        name=_as_str(raw.get("name"), "destinations.name"),
        postal_code=_as_str(raw.get("postal_code"), "destinations.postal_code"),
    )


def _parse(data: dict[str, Any]) -> AppConfig:
    api_raw = data.get("api") or {}
    quote_raw = data.get("quote") or {}
    products_raw = data.get("products") or []
    destinations_raw = data.get("destinations") or []

    if not isinstance(products_raw, list) or not products_raw:
        raise ValueError("config must define at least one [[products]] entry")
    if not isinstance(destinations_raw, list) or not destinations_raw:
        raise ValueError("config must define at least one [[destinations]] entry")

    usd_brl_rate = _as_float(quote_raw.get("usd_brl_rate"), "quote.usd_brl_rate")
    if usd_brl_rate <= 0:
        raise ValueError("quote.usd_brl_rate must be > 0")

    return AppConfig(
        api=ApiConfig(
            base_url=_as_str(api_raw.get("base_url"), "api.base_url").rstrip("/"),
            token=_as_str(api_raw.get("token"), "api.token"),
            user_agent=_as_str(api_raw.get("user_agent"), "api.user_agent"),
        ),
        quote=QuoteConfig(
            from_postal_code=_as_str(
                quote_raw.get("from_postal_code"), "quote.from_postal_code"
            ),
            services=_as_str(quote_raw.get("services"), "quote.services"),
            use_insurance_value=_as_bool(
                quote_raw.get("use_insurance_value", True),
                "quote.use_insurance_value",
            ),
            max_insurance_value_brl=_as_float(
                quote_raw.get("max_insurance_value_brl"),
                "quote.max_insurance_value_brl",
            ),
            usd_brl_rate=usd_brl_rate,
            output_currency=_parse_output_currency(
                quote_raw.get("output_currency", "BRL")
            ),
        ),
        products=tuple(_parse_product(item) for item in products_raw),
        destinations=tuple(_parse_destination(item) for item in destinations_raw),
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
    """Load local config.toml if present; otherwise config.toml.example."""
    local_path = config_path or _DEFAULT_CONFIG_PATH
    fallback_path = example_path or _EXAMPLE_CONFIG_PATH

    if local_path.is_file():
        return _parse(_load_toml(local_path))
    if fallback_path.is_file():
        return _parse(_load_toml(fallback_path))
    raise FileNotFoundError(
        f"No config found at {local_path} or {fallback_path}"
    )
