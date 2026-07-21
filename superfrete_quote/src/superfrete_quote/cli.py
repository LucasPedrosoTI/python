"""Argparse CLI entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from superfrete_quote.client import SuperFreteClient
from superfrete_quote.config import load_config
from superfrete_quote.csv_export import write_quotes_csv
from superfrete_quote.quote import run_quotes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="superfrete-quote",
        description=(
            "Quote Starlink kit freight via SuperFrete for Brazilian destinations "
            "and write a CSV table."
        ),
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help="Path to config.toml (default: project config.toml or example)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("quotes.csv"),
        help="Output CSV path (default: quotes.csv)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except (OSError, ValueError, TypeError) as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    if config.api.token in {"", "REPLACE_ME"}:
        print(
            "config error: set api.token in config.toml "
            "(copy from config.toml.example)",
            file=sys.stderr,
        )
        return 2

    client = SuperFreteClient(
        base_url=config.api.base_url,
        token=config.api.token,
        user_agent=config.api.user_agent,
    )

    print(
        f"Quoting {len(config.products)} products × "
        f"{len(config.destinations)} destinations "
        f"(output_currency={config.quote.output_currency})...",
        file=sys.stderr,
    )
    result = run_quotes(config, client, progress=sys.stderr)
    write_quotes_csv(args.output, result.rows, config.products)
    print(f"Wrote {args.output}", file=sys.stderr)

    if result.failure_count:
        print(
            f"{result.failure_count} quote(s) failed; see errors above.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
