# SuperFrete Quote CLI

CLI that quotes Starlink kit freight (Managed, Light, Fixed Wireless) via the [SuperFrete calculator API](https://superfrete.readme.io/reference/cotacao-de-frete) for all Brazilian state capitals and writes a CSV table.

## Setup

```bash
cd superfrete_quote
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp config.toml.example config.toml
```

1. Create a sandbox token at [sandbox integrations](https://sandbox.superfrete.com/#/integrations).
2. Set `api.token` in `config.toml`.
3. Adjust `quote.usd_brl_rate` and `quote.output_currency` (`BRL` or `USD`) as needed.

**Note:** Loggi only appears when there is a Loggi drop-off near the origin CEP. Enable Loggi on the token in SuperFrete integrations if needed.

## Run

```bash
python -m superfrete_quote --output quotes.csv
# or
superfrete-quote -o quotes.csv
```

Progress goes to stderr; the CSV is written to `--output`.

### Config highlights

| Key | Default | Meaning |
|-----|---------|---------|
| `api.base_url` | sandbox `/api/v0` | SuperFrete API base |
| `quote.from_postal_code` | `08538300` | Origin CEP |
| `quote.services` | `31` | Service codes (comma-separated, e.g. `1,2,31`). One CSV row per service per destination |
| `quote.use_insurance_value` | `true` | Include declared value |
| `quote.max_insurance_value_brl` | `3000` | Cap (Loggi limit) |
| `quote.usd_brl_rate` | `5.50` | FX for insurance USD→BRL and CSV BRL→USD |
| `quote.output_currency` | `BRL` | CSV price columns: `BRL` or `USD` |

Insurance:

- Managed / Light: R$ 3.000 (capped).
- Fixed Wireless: US$ 350 × `usd_brl_rate`, then capped at `max_insurance_value_brl`.

## CSV columns

`Destination`, `Managed  (41.84 lb / 18.98 kg)`, `Light  (35.41 lb / 16.06 kg)`, `Fixed Wireless  (6.83 lb / 3.10 kg)`, `Carrier / Service`, `Transit Time (days)`

## Tests

```bash
pytest
```
