"""CPF generation and validation (Mod-11 check digits)."""

from __future__ import annotations

import random
import re

_CPF_LENGTH = 11
_DIGITS_ONLY = re.compile(r"^\d+$")


def _is_all_same_digit(digits: str) -> bool:
    return len(digits) > 0 and digits == digits[0] * len(digits)


def _mod11_check_digit(digits: str, weights: list[int]) -> int:
    total = sum(int(d) * w for d, w in zip(digits, weights, strict=True))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def calculate_check_digits(base9: str) -> str:
    """Return the two CPF check digits for a 9-digit base."""
    if len(base9) != 9 or not _DIGITS_ONLY.fullmatch(base9):
        raise ValueError("CPF base must be exactly 9 digits")
    d1 = _mod11_check_digit(base9, list(range(10, 1, -1)))
    d2 = _mod11_check_digit(base9 + str(d1), list(range(11, 1, -1)))
    return f"{d1}{d2}"


def is_valid(cpf: str) -> bool:
    """Return True if cpf is 11 digits with valid check digits (not all same)."""
    if len(cpf) != _CPF_LENGTH or not _DIGITS_ONLY.fullmatch(cpf):
        return False
    if _is_all_same_digit(cpf):
        return False
    return cpf[-2:] == calculate_check_digits(cpf[:9])


def generate(rng: random.Random | None = None) -> str:
    """Generate a random valid 11-digit CPF (digits only)."""
    rng = rng or random.Random()
    while True:
        base9 = "".join(str(rng.randint(0, 9)) for _ in range(9))
        if _is_all_same_digit(base9):
            continue
        cpf = base9 + calculate_check_digits(base9)
        if is_valid(cpf):
            return cpf
