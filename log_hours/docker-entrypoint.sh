#!/bin/bash
set -e

echo "🚀 Starting Work Logger container..."

# Create log directory if it doesn't exist
mkdir -p /app/logs /app/screenshots

# Print environment info (without sensitive data)
echo "📋 Environment:"
echo "  - Python: $(python --version)"
echo "  - Playwright: $(python -c 'import playwright; print(playwright.__version__)')"
echo "  - Working directory: $(pwd)"

# Test application import
echo "🧪 Testing script execution with --help..."
python src/loghours.py --help

# If running in interactive mode or specific command provided, execute it
if [ "$#" -gt 0 ]; then
    echo "📝 Executing command: $*"
    exec "$@"
else
    CRON_SCHEDULE_VALUE="${CRON_SCHEDULE:-0 10 * * 5}"
    echo "⏰ Setting up cron job with schedule: $CRON_SCHEDULE_VALUE..."
    
    # Export environment variables to a file that cron can source
    echo "📝 Exporting environment variables for cron..."
    printenv | grep -E '^(JIRA_|WHATSAPP_|SYSTEM_|PYTHONPATH|PYTHONUNBUFFERED|PATH)' > /app/.env.cron
    
    # Show what environment variables were exported (without revealing sensitive values)
    echo "📋 Exported environment variables:"
    cat /app/.env.cron | sed 's/=.*/=***/' | sort
    
    # Create cron job with proper environment loading
    # The cron job will:
    # 1. Source the environment variables
    # 2. Set PYTHONPATH explicitly
    # 3. Change to /app directory
    # 4. Run the Python script
    (
        echo "# Work Logger Cron Job"
        echo "${CRON_SCHEDULE_VALUE} . /app/.env.cron && export PYTHONPATH=/app && cd /app && python src/loghours.py >> /app/logs/cronjob.log 2>&1"
    ) | crontab -
    
    # Verify cron job
    echo "📋 Cron job installed:"
    crontab -l
    
    # Start cron daemon
    echo "🔄 Starting cron daemon..."
    cron
    
    # Keep container running and show periodic status
    echo "✅ Container started successfully!"
    echo "📅 Work logger scheduled with: ${CRON_SCHEDULE_VALUE}"
    echo "📝 Container will log status every hour..."
    
    # Create a loop to keep container running and show periodic status
    while true; do
        echo "$(date): ✅ Work Logger container is running (PID: $$)"
        
        # Check if cron is still running
        if ! pgrep -f cron >/dev/null; then
            echo "⚠️ Cron daemon stopped, restarting..."
            cron
        fi
        
        # Log system resource usage periodically  
        if [ $(($(date +%s) % 21600)) -eq 0 ]; then  # Every 6 hours
            echo "📊 System stats: $(free -h | grep Mem | awk '{print "Memory: " $3 "/" $2}')"
            echo "📅 Schedule: ${CRON_SCHEDULE_VALUE}"
        fi
        
        sleep 43200  # Log status every 12 hours
    done
fi 