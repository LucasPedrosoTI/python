# Automated Work Logger 🤖

Automates work hours logging to service management systems using Playwright web automation. **Runs on configurable schedule** (defaults to Friday at 10:00 AM) when deployed.

## Quick Start

```bash
cd log_hours

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Manual Run
python src/loghours.py
```

## Features

- 🎭 **Playwright automation** - Modern, reliable web automation (migrated from Selenium)
- 📱 **Responsive design** - Auto-sets viewport to 1366x768 for site compatibility
- 🛡️ **Smart error handling** - Multiple fallback selectors + debug screenshots
- 🐳 **Docker ready** - Containerized deployment with CI/CD pipeline
- 📦 **Simple dependencies** - Standard pip + requirements.txt (no Poetry conflicts)
- ⏰ **Automated scheduling** - Configurable cron schedule (defaults to Friday at 10:00 AM)

## Setup

### Development
```bash
pip install -r requirements-dev.txt
playwright install chromium
```

## Usage

### Local Development
```bash
source venv/bin/activate
python src/loghours.py
``
### Options
```bash
# Log full week (Monday-Friday)
python src/loghours.py

# Log only today's hours
python src/loghours.py --today

# Log specific day
python src/loghours.py --day Mo  # Monday
python src/loghours.py --day We  # Wednesday

# Log day intervals
python src/loghours.py --interval Tu-Fr  # Tuesday through Friday
python src/loghours.py --interval Mo-We  # Monday through Wednesday

# Override existing hours (default: skip days with existing hours)
python src/loghours.py --today --override   # Force relog today
python src/loghours.py --interval Tu-Fr -o  # Force relog interval
python src/loghours.py -o                   # Force relog entire week

# With/Without Browser
python src/loghours.py --today --headless
python src/loghours.py --today --no-headless
```

### Docker
```bash
# Build and run with default schedule (Friday 10 AM)
docker build -t log-hours .
docker run -d --name work-logger log-hours

# Build and run with custom schedule (daily at 2 PM)
docker run -d --name work-logger -e CRON_SCHEDULE="0 14 * * *" log-hours

# View logs
docker logs work-logger

# Run manually (override cron)
docker run --rm log-hours python src/loghours.py --today
```

## Deployment Behavior

### 🗓️ **Automated Schedule:**
- **Default:** Every Friday at 10:00 AM (`0 10 * * 5`)
- **Configurable:** Set `CRON_SCHEDULE` environment variable
- **Logs:** Full week (Monday-Friday) hours
- **Location:** `/app/logs/cronjob.log` inside container

### ⚙️ **Environment Variables:**
- `CRON_SCHEDULE` - Cron expression for scheduling (default: `0 10 * * 5`)
  - Examples: `0 14 * * *` (daily 2 PM), `0 9 * * 1-5` (weekdays 9 AM)

### 📋 **Container Status:**
- **Runs continuously** with cron daemon
- **Auto-restarts** if container crashes
- **Health checks** every 30 seconds
- **Status logs** every hour

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
| Cron not running | Check container logs: `docker logs work-logger` |
| Wrong schedule | Verify cron: `docker exec work-logger crontab -l` |

## CI/CD

GitHub Actions workflow automatically:
- Tests on push to `log_hours/` directory
- Builds Docker image and pushes to DockerHub
- Deploys to VPS via SSH

**Required secrets:** `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `VPS_SSH_KEY`, `VPS_HOST`, `VPS_USER` 