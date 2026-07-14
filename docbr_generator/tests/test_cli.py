"""CLI tests (one scenario per test)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from docbr_generator.cli import main
from docbr_generator.config import load_config


def test_cli_cpf_prints_eleven_digits(capsys) -> None:
    exit_code = main(["cpf"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip().isdigit()
    assert len(captured.out.strip()) == 11
    assert captured.err == ""


def test_cli_cnpj_prints_fourteen_digits(capsys) -> None:
    exit_code = main(["cnpj"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip().isdigit()
    assert len(captured.out.strip()) == 14
    assert captured.err == ""


def test_cli_rejects_unknown_document() -> None:
    try:
        main(["rg"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("expected SystemExit for invalid document type")


def test_cli_paste_copies_and_simulates_cmd_v(capsys) -> None:
    completed = MagicMock(returncode=0, stderr=b"")
    with (
        patch("docbr_generator.cli.subprocess.run", return_value=completed) as run_mock,
        patch("docbr_generator.cli.time.sleep"),
    ):
        exit_code = main(["cpf", "--paste"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(captured.out.strip()) == 11
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[0] == ["pbcopy"]
    assert run_mock.call_args_list[1].args[0][:2] == ["osascript", "-e"]


def test_load_config_falls_back_to_example(tmp_path: Path) -> None:
    example = tmp_path / "config.toml.example"
    example.write_text(
        '[output]\ndigits_only = true\n\n[cli]\npython_path = "/tmp/example-python"\n',
        encoding="utf-8",
    )
    missing_local = tmp_path / "config.toml"
    config = load_config(missing_local, example_path=example)
    assert config.output.digits_only is True
    assert config.cli.python_path == "/tmp/example-python"


def test_load_config_prefers_local_over_example(tmp_path: Path) -> None:
    example = tmp_path / "config.toml.example"
    example.write_text(
        '[cli]\npython_path = "/tmp/example-python"\n',
        encoding="utf-8",
    )
    local = tmp_path / "config.toml"
    local.write_text(
        '[cli]\npython_path = "/tmp/local-python"\n',
        encoding="utf-8",
    )
    config = load_config(local, example_path=example)
    assert config.cli.python_path == "/tmp/local-python"
