"""CNPJ generator and validator tests (one scenario per test)."""

from __future__ import annotations

import random

from docbr_generator import cnpj


def test_generate_returns_fourteen_digits() -> None:
    value = cnpj.generate(random.Random(1))
    assert len(value) == 14
    assert value.isdigit()


def test_generate_has_valid_check_digits() -> None:
    value = cnpj.generate(random.Random(2))
    assert cnpj.is_valid(value)


def test_generate_is_not_all_same_digit() -> None:
    value = cnpj.generate(random.Random(3))
    assert value != value[0] * 14


def test_generate_uses_branch_0001() -> None:
    value = cnpj.generate(random.Random(4))
    assert value[8:12] == "0001"


def test_is_valid_accepts_known_valid_cnpj() -> None:
    # Base 112223330001 → check digits 81
    assert cnpj.is_valid("11222333000181")


def test_is_valid_rejects_wrong_check_digits() -> None:
    assert not cnpj.is_valid("11222333000100")


def test_is_valid_rejects_all_same_digits() -> None:
    assert not cnpj.is_valid("00000000000000")


def test_is_valid_rejects_wrong_length() -> None:
    assert not cnpj.is_valid("1122233300018")


def test_is_valid_rejects_non_digits() -> None:
    assert not cnpj.is_valid("1122233300018a")


def test_calculate_check_digits_for_known_base() -> None:
    assert cnpj.calculate_check_digits("112223330001") == "81"
