# Automated Work Logger 🤖

Automates work hours logging to service management systems using Playwright web automation.

## Quick Start

```bash
cd log_hours

# Setup
python3 -m venv venv
source venv/bin/activate
pip install --index-url https://pypi.org/simple -r requirements.txt
playwright install chromium

# Run
python src/loghours.py
```

## Features

- 🎭 **Playwright automation** - Modern, reliable web automation (migrated from Selenium)
- 📱 **Responsive design** - Auto-sets viewport to 1366x768 for site compatibility
- 🛡️ **Smart error handling** - Multiple fallback selectors + debug screenshots
- 🐳 **Docker ready** - Containerized deployment with CI/CD pipeline
- 📦 **Simple dependencies** - Standard pip + requirements.txt (no Poetry conflicts)

## Setup

### Development
```bash
pip install --index-url https://pypi.org/simple -r requirements-dev.txt
playwright install
```

## Usage

### Basic
```bash
source venv/bin/activate
python src/loghours.py
```

### Options
```bash
# Log full week (Monday-Friday)
python src/loghours.py

# Log only today's hours
python src/loghours.py --today

# Log specific day
python src/loghours.py --day Mo  # Monday
python src/loghours.py --day We  # Wednesday
```

### Docker
```bash
# Build and run
docker build -t log-hours .
docker run --rm -v $(pwd)/screenshots:/app/screenshots log-hours

# Or use compose
docker compose up
```

## Project Structure

```
log_hours/
├── src/loghours.py          # Main automation script
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-container setup
└── .github/workflows/      # CI/CD pipeline
```

## Dependencies

**Production:** `playwright`, `python-dotenv`, `requests`
**Development:** Adds `pytest`, `black`, `flake8`, `isort`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Activate virtual environment: `source venv/bin/activate` |
| Browser not launching | Run: `playwright install chromium` |
| Timeout/element errors | Check `debug_screenshot.png` for page state |
| Repository conflicts | Use `--index-url https://pypi.org/simple` |

## CI/CD

GitHub Actions workflow automatically:
- Tests on push to `log_hours/` directory
- Builds Docker image and pushes to DockerHub
- Deploys to VPS via SSH

**Required secrets:** `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `VPS_SSH_KEY`, `VPS_HOST`, `VPS_USER` 