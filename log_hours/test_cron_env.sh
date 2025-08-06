#!/bin/bash
# Test script to simulate cron environment

echo "=== Testing Cron Environment Setup ==="
echo ""

# Check if .env.cron exists
if [ -f /app/.env.cron ]; then
    echo "✅ Environment file exists: /app/.env.cron"
    echo "📋 Contents (masked):"
    cat /app/.env.cron | sed 's/export //' | sed 's/=.*/=***/' | sort
    echo ""
    echo "📋 Format check (first 3 lines):"
    head -n 3 /app/.env.cron | sed 's/=".*$/="***"/'
    echo ""
else
    echo "❌ Environment file not found: /app/.env.cron"
    echo "   Run docker-entrypoint.sh first to create it"
    exit 1
fi

# Simulate cron environment (minimal environment)
echo "=== Simulating Cron Environment ==="
env -i /bin/bash -c '
    echo "Initial environment (should be minimal):"
    echo "  PATH=$PATH"
    echo "  PYTHONPATH=$PYTHONPATH"
    echo ""
    
    echo "Sourcing environment variables..."
    . /app/.env.cron
    export PYTHONPATH=/app
    
    echo "After sourcing:"
    echo "  PATH=$PATH"
    echo "  PYTHONPATH=$PYTHONPATH"
    echo "  JIRA_USERNAME=$JIRA_USERNAME"
    echo "  WHATSAPP_ENABLED=$WHATSAPP_ENABLED"
    echo ""
    
    echo "Testing Python can see environment variables..."
    cd /app
    python -c "import os; print(f\"  Python sees JIRA_USERNAME: {os.getenv('JIRA_USERNAME', 'NOT SET')}\")"
    python -c "import os; print(f\"  Python sees PYTHONPATH: {os.getenv('PYTHONPATH', 'NOT SET')}\")"
    echo ""
    
    echo "Testing full script execution..."
    python src/loghours.py --help 2>&1 | head -n 3
    echo ""
    
    echo "Testing with --today flag..."
    python src/loghours.py --today
'

echo ""
echo "=== Test Complete ==="