#!/bin/bash
# Script to test the exact command that cron will run

echo "=== Testing Exact Cron Command ==="
echo ""
echo "This simulates exactly what cron will execute:"
echo ". /app/.env.cron && export PYTHONPATH=/app && cd /app && python src/loghours.py"
echo ""
echo "Running..."
echo "----------------------------------------"

# Execute the exact command that cron will run
. /app/.env.cron && export PYTHONPATH=/app && cd /app && python src/loghours.py --today

echo "----------------------------------------"
echo "✅ Test complete!"
echo ""
echo "If this works, the cron job should work too."
echo "To see the actual cron job, run: crontab -l"