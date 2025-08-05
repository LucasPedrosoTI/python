#!/bin/bash
# Test script to simulate cron environment

echo "=== Testing Cron Environment Setup ==="
echo ""

# Check if .env.cron exists
if [ -f /app/.env.cron ]; then
    echo "✅ Environment file exists: /app/.env.cron"
    echo "📋 Contents (masked):"
    cat /app/.env.cron | sed 's/=.*/=***/' | sort
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
    echo ""
    
    echo "Testing Python import..."
    cd /app
    python src/loghours.py --help 
    python src/loghours.py --wp-test 
'

echo ""
echo "=== Test Complete ==="