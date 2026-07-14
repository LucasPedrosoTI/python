"""CPF generator and validator tests (one scenario per test)."""

from __future__ import annotations

import random

from docbr_generator import cpf


def test_generate_returns_eleven_digits() -> None:
    value = cpf.generate(random.Random(1))
    assert len(value) == 11
    assert value.isdigit()


def test_generate_has_valid_check_digits() -> None:
    value = cpf.generate(random.Random(2))
    assert cpf.is_valid(value)


def test_generate_is_not_all_same_digit() -> None:
    value = cpf.generate(random.Random(3))
    assert value != value[0] * 11


def test_is_valid_accepts_known_valid_cpf() -> None:
    # Base 529982247 → check digits 25
    assert cpf.is_valid("52998224725")


def test_is_valid_rejects_wrong_check_digits() -> None:
    assert not cpf.is_valid("52998224700")


def test_is_valid_rejects_all_same_digits() -> None:
    assert not cpf.is_valid("11111111111")


def test_is_valid_rejects_wrong_length() -> None:
    assert not cpf.is_valid("5299822472")


def test_is_valid_rejects_non_digits() -> None:
    assert not cpf.is_valid("5299822472a")


def test_calculate_check_digits_for_known_base() -> None:
    assert cpf.calculate_check_digits("529982247") == "25"
