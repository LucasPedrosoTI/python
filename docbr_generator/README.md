# DocBR Generator

Generate algorithmically valid Brazilian **CPF** and **CNPJ** numbers (digits only) for local form/dev testing. Designed to be triggered from **macOS Shortcuts (Atalhos)** so a keyboard shortcut pastes a value into the focused field.

**Disclaimer:** Generated numbers pass Mod-11 check digits only. They are **not** registered with Receita Federal and must not be used as real identity documents.

## Requirements

- Python 3.11+
- macOS (for Shortcuts / Atalhos + clipboard paste)

## Setup

```bash
cd ~/dev/python/docbr_generator
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" --index-url https://pypi.org/simple
cp config.toml.example config.toml   # optional local overrides
```

Edit `config.toml` if you want a machine-specific `python_path` for Shortcuts. Do not commit `config.toml` (it is gitignored).

## Run

```bash
# Print digits only
python -m docbr_generator cpf
python -m docbr_generator cnpj

# Copy to clipboard (macOS)
python -m docbr_generator cpf --copy

# Copy and paste into the focused field (needs Accessibility)
python -m docbr_generator cpf --paste
python -m docbr_generator cnpj --paste
```

Installed console script (same behavior):

```bash
docbr-generator cpf
docbr-generator cnpj --paste
```

## Test

```bash
source .venv/bin/activate
pytest
```

## macOS Shortcuts / Atalhos (pt-BR)

You only need **one** action: **Executar Script Shell**.  
Do **not** look for Colar/Paste or AppleScript in the shortcut — `--paste` does copy + Cmd+V for you.

### 1. Create the CPF shortcut

1. Open **Atalhos**.
2. Click **+** to create a new shortcut.
3. Search for **Executar Script Shell** and add it.
4. Set the shell to **zsh** (or leave the default).
5. Replace the script body with (update `YOUR_USER`):

```bash
"/Users/YOUR_USER/dev/python/docbr_generator/.venv/bin/python" -m docbr_generator cpf --paste
```

6. Tap the shortcut name at the top → rename to **Gerar CPF**.
7. Tap the **ⓘ** (or shortcut details) → **Adicionar Atalho de Teclado** → set **⌃⌥C** (Control-Option-C).
8. Under details, turn **on** “Usar com” / run while another app is focused if that option appears (so the hotkey works globally).

### 2. Create the CNPJ shortcut

Same steps, script:

```bash
"/Users/YOUR_USER/dev/python/docbr_generator/.venv/bin/python" -m docbr_generator cnpj --paste
```

Suggested name: **Gerar CNPJ**. Suggested hotkey: **⌃⌥J**.

### 3. Permissions (required for paste)

1. Open **Ajustes do Sistema → Privacidade e Segurança → Acessibilidade**.
2. Enable **Atalhos** (and if prompted, **osascript** / **Terminal**).
3. Click a text field in any app, press your hotkey — the digits should appear.

If paste fails, the CLI prints an error about Accessibility on stderr; re-check that toggle and try again.

### Why not “Colar”?

In many pt-BR Shortcut libraries there is no reliable **Colar** action for “paste into the frontmost app”. Using `--paste` avoids a second action and avoids writing AppleScript by hand.

## Configuration

| File | Tracked | Purpose |
|------|---------|---------|
| `config.toml.example` | Yes | Safe defaults / documentation |
| `config.toml` | No | Local overrides (paths, etc.) |

Load order: local `config.toml` if present, else `config.toml.example`, else code defaults.

## License / use

For personal/dev testing only. Do not submit generated documents as real CPF/CNPJ.
