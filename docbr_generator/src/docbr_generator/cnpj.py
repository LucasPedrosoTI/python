"""CNPJ generation and validation (Mod-11 check digits)."""

from __future__ import annotations

import random
import re

_CNPJ_LENGTH = 14
_DIGITS_ONLY = re.compile(r"^\d+$")
_WEIGHTS_D1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_WEIGHTS_D2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _is_all_same_digit(digits: str) -> bool:
    return len(digits) > 0 and digits == digits[0] * len(digits)


def _mod11_check_digit(digits: str, weights: list[int]) -> int:
    total = sum(int(d) * w for d, w in zip(digits, weights, strict=True))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def calculate_check_digits(base12: str) -> str:
    """Return the two CNPJ check digits for a 12-digit base."""
    if len(base12) != 12 or not _DIGITS_ONLY.fullmatch(base12):
        raise ValueError("CNPJ base must be exactly 12 digits")
    d1 = _mod11_check_digit(base12, _WEIGHTS_D1)
    d2 = _mod11_check_digit(base12 + str(d1), _WEIGHTS_D2)
    return f"{d1}{d2}"


def is_valid(cnpj: str) -> bool:
    """Return True if cnpj is 14 digits with valid check digits (not all same)."""
    if len(cnpj) != _CNPJ_LENGTH or not _DIGITS_ONLY.fullmatch(cnpj):
        return False
    if _is_all_same_digit(cnpj):
        return False
    return cnpj[-2:] == calculate_check_digits(cnpj[:12])


def generate(rng: random.Random | None = None) -> str:
    """Generate a random valid 14-digit CNPJ (digits only)."""
    rng = rng or random.Random()
    while True:
        # Common pattern: random 8-digit root + branch 0001
        root = "".join(str(rng.randint(0, 9)) for _ in range(8))
        if _is_all_same_digit(root):
            continue
        base12 = root + "0001"
        cnpj = base12 + calculate_check_digits(base12)
        if is_valid(cnpj):
            return cnpj
