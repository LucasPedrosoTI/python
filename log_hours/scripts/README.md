# Test Scripts

This folder contains utility scripts for testing and debugging the Work Logger application in containerized environments.

## Scripts

### `test_cron_env.sh`
Tests the cron environment setup by simulating the minimal environment that cron provides.

**What it does:**
- Verifies `.env.cron` file exists and is properly formatted
- Simulates cron's minimal environment using `env -i`
- Tests that environment variables are properly loaded and exported
- Runs the work logger script to verify everything works

**Usage:**
```bash
# Inside the container
bash /app/scripts/test_cron_env.sh

# From outside the container
docker exec work-logger bash /app/scripts/test_cron_env.sh
```

### `test_cron_job.sh`
Tests the exact command that the cron job will execute.

**What it does:**
- Simulates the exact cron command: `. /app/.env.cron && export PYTHONPATH=/app && cd /app && python src/loghours.py`
- Uses `--today` flag for quick testing without running a full week

**Usage:**
```bash
# Inside the container
bash /app/scripts/test_cron_job.sh

# From outside the container
docker exec work-logger bash /app/scripts/test_cron_job.sh
```

## When to Use

- **After rebuilding the container** to verify environment setup
- **When debugging cron issues** to isolate environment problems
- **Before deploying** to ensure the scheduled job will work
- **When troubleshooting** Playwright or dependency issues

## Troubleshooting

If tests fail:
1. Check that the container started properly: `docker compose ps`
2. Verify environment variables in `.env` file
3. Ensure Playwright browsers are installed: `docker exec work-logger python -m playwright install --list`
4. Check container logs: `docker compose logs`