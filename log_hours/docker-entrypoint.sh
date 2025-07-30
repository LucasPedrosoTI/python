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
echo "🧪 Testing application import..."
python -c "from src.automated_work_logger import AutomatedWorkLogger; print('✅ Application import successful')"

# If running in interactive mode or specific command provided, execute it
if [ "$#" -gt 0 ]; then
    echo "📝 Executing command: $*"
    exec "$@"
else
    echo "⏰ Setting up cron job with schedule: ${CRON_SCHEDULE:-0 10 * * 5}..."
    
    # Create cron job with configurable schedule (defaults to Friday 10 AM)
    echo "${CRON_SCHEDULE:-0 10 * * 5} cd /app && python src/loghours.py >> /app/logs/cronjob.log 2>&1" | crontab -
    
    # Verify cron job
    echo "📋 Cron job installed:"
    crontab -l
    
    # Start cron daemon
    echo "🔄 Starting cron daemon..."
    cron
    
    # Keep container running and show periodic status
    echo "✅ Container started successfully!"
    echo "📅 Work logger scheduled with: ${CRON_SCHEDULE:-0 10 * * 5}"
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
            echo "📅 Schedule: ${CRON_SCHEDULE:-0 10 * * 5}"
        fi
        
        sleep 3600  # Log status every hour
    done
fi 