#!/bin/bash
set -e

echo "🔧 Docker Container Starting..."
echo "================================"

# Check Python version
echo "Python version:"
python --version

# Check working directory
echo ""
echo "Working directory: $(pwd)"

# Check if iqoptionapi exists
echo ""
echo "Checking iqoptionapi folder:"
if [ -d "/app/iqoptionapi" ]; then
    echo "✅ iqoptionapi folder exists"
    ls -la /app/iqoptionapi/ | head -10
else
    echo "❌ iqoptionapi folder NOT found!"
    exit 1
fi

# Check PYTHONPATH
echo ""
echo "PYTHONPATH: $PYTHONPATH"

# Test import
echo ""
echo "Testing iqoptionapi import..."
python -c "from iqoptionapi.stable_api import IQ_Option; print('✅ iqoptionapi import successful')" || {
    echo "❌ Failed to import iqoptionapi!"
    echo "Python path:"
    python -c "import sys; print('\n'.join(sys.path))"
    exit 1
}

echo ""
echo "================================"
echo "🚀 All checks passed! Starting application..."
echo ""

# Execute the main command
exec "$@"
