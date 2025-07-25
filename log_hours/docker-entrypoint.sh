#!/bin/bash
set -e

echo "🚀 Starting Work Logger container..."
echo "📦 Image: $(cat /etc/hostname) - $(date)"

# Set up cron job inside container
echo "⏰ Setting up cron job..."
echo "0 10 * * 5 cd /app && python src/loghours.py >> /app/logs/cronjob.log 2>&1" | crontab -

# Verify cron job
echo "📋 Cron job installed:"
crontab -l

# Start cron daemon
echo "🔄 Starting cron daemon..."
sudo cron

# Test application on startup
echo "🧪 Testing application..."
python -c "from src.loghours import AutomatedWorkLogger; print('✅ Application test passed')"

# Keep container running and show periodic status
echo "✅ Container started successfully!"
echo "📝 Container will log status every hour..."

# Create a loop to keep container running and show periodic status
while true; do
    echo "$(date): ✅ Work Logger container is running (PID: $$)"
    
    # Check if cron is still running
    if ! pgrep -f cron >/dev/null; then
        echo "⚠️ Cron daemon stopped, restarting..."
        sudo cron
    fi
    
    # Log system resource usage periodically
    if [ $(($(date +%s) % 21600)) -eq 0 ]; then  # Every 6 hours
        echo "📊 System stats: $(free -h | grep Mem | awk '{print "Memory: " $3 "/" $2}')"
    fi
    
    sleep 3600  # Log status every hour
done 