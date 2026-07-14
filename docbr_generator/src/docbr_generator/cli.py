"""CLI entrypoint for generating CPF/CNPJ values."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

from docbr_generator import cnpj, cpf
from docbr_generator.config import load_config

_PASTE_APPLESCRIPT = (
    'tell application "System Events" to keystroke "v" using command down'
)


def _copy_to_clipboard(value: str) -> None:
    """Copy digits to the macOS clipboard via pbcopy (no trailing newline)."""
    process = subprocess.run(
        ["pbcopy"],
        input=value.encode("utf-8"),
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        err = process.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(err or "pbcopy failed")


def _paste_from_clipboard(*, delay_seconds: float = 0.15) -> None:
    """Simulate Cmd+V via System Events (requires Accessibility permission)."""
    # Brief pause so the clipboard is ready and Shortcuts has released focus.
    time.sleep(delay_seconds)
    process = subprocess.run(
        ["osascript", "-e", _PASTE_APPLESCRIPT],
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        err = process.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(err or "osascript paste failed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docbr-generator",
        description="Generate algorithmically valid Brazilian CPF/CNPJ numbers (digits only).",
    )
    parser.add_argument(
        "document",
        choices=("cpf", "cnpj"),
        help="Document type to generate",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Also copy the result to the clipboard (macOS pbcopy)",
    )
    parser.add_argument(
        "--paste",
        action="store_true",
        help="Copy to clipboard and paste into the focused field (Cmd+V via AppleScript)",
    )
    return parser


def generate_document(document: str) -> str:
    if document == "cpf":
        return cpf.generate()
    if document == "cnpj":
        return cnpj.generate()
    raise ValueError(f"Unsupported document type: {document}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Config is loaded for future overrides / Shortcuts path docs; output is always digits.
    load_config()

    value = generate_document(args.document)
    if not value.isdigit():
        print("generator produced non-digit output", file=sys.stderr)
        return 1

    if args.copy or args.paste:
        try:
            _copy_to_clipboard(value)
        except (OSError, RuntimeError) as exc:
            print(f"failed to copy to clipboard: {exc}", file=sys.stderr)
            return 1

    if args.paste:
        try:
            _paste_from_clipboard()
        except (OSError, RuntimeError) as exc:
            print(f"failed to paste: {exc}", file=sys.stderr)
            print(
                "Grant Accessibility to Terminal/Shortcuts/osascript under "
                "System Settings → Privacy & Security → Accessibility.",
                file=sys.stderr,
            )
            return 1

    # Single trailing newline for shell pipelines; digits-only payload.
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
