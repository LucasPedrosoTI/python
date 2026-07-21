"""SuperFrete HTTP calculator client (stdlib urllib)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QuoteResult:
    price: float
    carrier_service: str
    transit_days: int | None
    service_id: int | None = None

    @property
    def service_key(self) -> str:
        """Stable key for grouping one CSV row per service."""
        if self.service_id is not None:
            return str(self.service_id)
        return self.carrier_service


class SuperFreteError(Exception):
    """Raised when the SuperFrete API call or response cannot be used."""


class SuperFreteClient:
    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        user_agent: str,
        timeout_s: float = 30.0,
        max_retries: int = 3,
        retry_backoff_s: float = 1.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._user_agent = user_agent
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._retry_backoff_s = retry_backoff_s

    def calculate(self, payload: dict[str, Any]) -> list[QuoteResult]:
        url = f"{self._base_url}/calculator"
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._token}",
                "User-Agent": self._user_agent,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                with urllib.request.urlopen(
                    request, timeout=self._timeout_s
                ) as response:
                    raw = response.read().decode("utf-8")
                    data = json.loads(raw)
                return parse_calculator_response(data)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in {429, 500, 502, 503, 504} and attempt + 1 < self._max_retries:
                    time.sleep(self._retry_backoff_s * (2**attempt))
                    continue
                detail = exc.read().decode("utf-8", errors="replace")
                raise SuperFreteError(
                    f"HTTP {exc.code} from SuperFrete: {detail}"
                ) from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt + 1 < self._max_retries:
                    time.sleep(self._retry_backoff_s * (2**attempt))
                    continue
                raise SuperFreteError(str(exc)) from exc

        raise SuperFreteError(str(last_error) if last_error else "unknown error")


def parse_calculator_response(data: Any) -> list[QuoteResult]:
    """Return all usable quotes from a calculator response (one per service)."""
    items = _normalize_quote_items(data)
    if not items:
        raise SuperFreteError("calculator response contained no quotes")

    results: list[QuoteResult] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("error") or item.get("has_error"):
            continue
        price = _extract_price(item)
        if price is None:
            continue
        results.append(
            QuoteResult(
                price=price,
                carrier_service=_extract_carrier_service(item),
                transit_days=_extract_transit_days(item),
                service_id=_as_optional_int(item.get("id") or item.get("service_id")),
            )
        )

    if results:
        return results

    errors = [
        str(item.get("error") or item.get("message") or item)
        for item in items
        if isinstance(item, dict)
    ]
    raise SuperFreteError(
        "no usable quote in response"
        + (f": {'; '.join(errors)}" if errors else "")
    )


def _normalize_quote_items(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "quotes", "results", "services"):
            nested = data.get(key)
            if isinstance(nested, list):
                return nested
        # Single quote object
        if "price" in data or "custom_price" in data or "id" in data:
            return [data]
    return []


def _extract_price(item: dict[str, Any]) -> float | None:
    for key in ("custom_price", "price"):
        value = item.get(key)
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _extract_carrier_service(item: dict[str, Any]) -> str:
    company = item.get("company")
    company_name = ""
    if isinstance(company, dict):
        company_name = str(company.get("name") or "").strip()
    service_name = str(item.get("name") or item.get("service") or "").strip()
    if company_name and service_name:
        return f"{company_name} / {service_name}"
    return company_name or service_name or "Unknown"


def _extract_transit_days(item: dict[str, Any]) -> int | None:
    for key in ("delivery_time", "delivery", "delivery_max", "custom_delivery_time"):
        value = item.get(key)
        if value is None or value == "":
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _as_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
