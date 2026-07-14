# AGENTS.md — DocBR Generator

Guidance for coding agents working in `docbr_generator`. Prefer this file for implementation detail; keep `README.md` user-facing and shorter.

## Purpose and placement

- Lives in the `~/dev/python` monorepo as `docbr_generator/` (sibling of `invoice_generator`, `log_hours`, `utils`).
- Generates **algorithmically valid** Brazilian CPF (11 digits) and CNPJ (14 digits), **digits only**, for local testing and macOS Shortcuts paste workflows.
- Numbers are **not** Receita Federal–registered. Never add network validation or scraping of government APIs.

## Package layout

| Path | Responsibility |
|------|----------------|
| `src/docbr_generator/cpf.py` | CPF Mod-11 check digits, `generate`, `is_valid` |
| `src/docbr_generator/cnpj.py` | CNPJ Mod-11 check digits, `generate`, `is_valid` |
| `src/docbr_generator/config.py` | TOML load: local `config.toml` → example → defaults |
| `src/docbr_generator/cli.py` | argparse CLI; stdout digits; `--copy` / `--paste` (pbcopy + Cmd+V) |
| `src/docbr_generator/__main__.py` | `python -m docbr_generator` entry |
| `tests/` | pytest; **one scenario per test** |

Project root for config resolution is two parents above `config.py` (`src/docbr_generator` → `src` → project root). Do not hardcode user home paths in source.

## CPF / CNPJ algorithms

### CPF

- 9 random base digits + 2 Mod-11 check digits → 11 digits.
- Weights for first check digit: 10..2; second: 11..2.
- Remainder `< 2` → check digit `0`; else `11 - remainder`.
- Reject all-same-digit sequences (e.g. `11111111111`) in both generation and validation.

### CNPJ

- Generator uses 8 random root digits + branch `0001` + 2 check digits → 14 digits.
- Weights d1: `[5,4,3,2,9,8,7,6,5,4,3,2]`; d2: `[6,5,4,3,2,9,8,7,6,5,4,3,2]`.
- Same Mod-11 rule and all-same-digit rejection as CPF.

When changing algorithms, update known-vector tests (`52998224725` CPF, `11222333000181` CNPJ).

## CLI contract

- Commands: `cpf` | `cnpj`; optional `--copy` and/or `--paste`.
- `--paste` implies copy, then `osascript` System Events Cmd+V (Accessibility required).
- **Stdout must be digits only** plus a single trailing newline (Shortcuts / `pbcopy` pipelines).
- Do not print logs, prompts, or formatting to stdout on success.
- Errors go to stderr; non-zero exit on failure.
- Do not add punctuation/format flags unless the product scope changes (currently out of scope).

## Config rules

- Commit `config.toml.example` only.
- Never commit `config.toml`, `.venv/`, or secrets (this project has no credentials today; keep it that way).
- `[cli].python_path` is documentation for Shortcuts setup; do not bake machine-specific paths into Python modules.
- If you add config keys, document them in both `config.toml.example` and README.

## Shortcuts integration

- Prefer a **single** Shortcuts action: **Executar Script Shell** with  
  `.venv/bin/python -m docbr_generator <type> --paste`  
  (no Colar/Paste action, no hand-written AppleScript in the shortcut).
- README documents pt-BR Atalhos labels; keep that when editing setup docs.
- Agents must **not** hardcode `/Users/...` paths in source or committed scripts.
- Document path placeholders as `YOUR_USER` in README.
- Accessibility for **Atalhos** is required for `--paste`; mention it when changing Shortcuts docs.

## Testing expectations

- Use pytest; keep **one scenario per test** (no combined success/failure cases in one test).
- Cover: length, digit-only output, valid check digits, all-same rejection, known vectors, CLI stdout, config load preference (local over example).
- Prefer injecting `random.Random(seed)` into `generate` for determinism where useful; CLI tests may use real RNG if they only assert shape/validity via length and `isdigit()`.

## Dependencies

- Runtime: stdlib only (`tomllib`, `argparse`, `subprocess`, `random`).
- Dev: `pytest` via `.[dev]`.
- This machine may point pip at Indeed’s private index; for public packages use `--index-url https://pypi.org/simple` or `uv` with a public index when installing.

## Out of scope

- Formatted output (`123.456.789-09`, `12.345.678/0001-95`)
- Raycast / Alfred / Keyboard Maestro / Hammerspoon
- Network validation or “real” document lookup
- Storing or shipping generated numbers as identity data

## When changing the monorepo root README

Update `~/dev/python/README.md` Contents and Projects sections if renaming/removing this package.
