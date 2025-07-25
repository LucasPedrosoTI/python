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
python -c "from loghours import TestLoghours; print('✅ Application import successful')"

# If running in interactive mode or specific command provided, execute it
if [ "$#" -gt 0 ]; then
    echo "📝 Executing command: $*"
    exec "$@"
else
    echo "🔄 Starting automated work logging..."
    # Default: run the automation
    exec python -m pytest loghours.py::TestLoghours::test_loghours -v
fi 