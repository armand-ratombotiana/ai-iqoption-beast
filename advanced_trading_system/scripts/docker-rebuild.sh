#!/bin/bash
# Rebuild Docker container with proper checks

set -e

echo "🔄 Rebuilding Docker Container..."
echo "=================================="
echo ""

# Pre-flight checks
echo "Running pre-flight checks..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found!"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found!"
    exit 1
fi

if [ ! -d "iqoptionapi" ]; then
    echo "❌ iqoptionapi folder not found!"
    exit 1
fi

echo "✅ All files present"
echo ""

# Stop and remove existing containers
echo "1. Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Remove old images
echo ""
echo "2. Removing old images..."
docker rmi kael-trading-system 2>/dev/null || true
docker image prune -f 2>/dev/null || true

# Build with no cache
echo ""
echo "3. Building new image (this may take 3-5 minutes)..."
echo "   Watch for these verification steps:"
echo "   - ✅ requests installed"
echo "   - ✅ numpy installed"
echo "   - ✅ websocket installed"
echo "   - ✅ iqoptionapi verified"
echo ""

docker-compose build --no-cache || {
    echo ""
    echo "❌ Build failed!"
    echo ""
    echo "Common issues:"
    echo "  - Check if requirements.txt has all dependencies"
    echo "  - Ensure iqoptionapi folder is not empty"
    echo "  - Check Docker logs above for specific errors"
    exit 1
}

# Verify the build
echo ""
echo "4. Verifying iqoptionapi in built image..."
docker run --rm kael-trading-system python -c "
import sys
print('Python version:', sys.version.split()[0])
print('')
from iqoptionapi.stable_api import IQ_Option
print('✅ iqoptionapi successfully imported!')
" || {
    echo "❌ Verification failed!"
    exit 1
}

echo ""
echo "=================================="
echo "✅ Build successful!"
echo ""
echo "Next steps:"
echo ""
echo "  Start container:"
echo "    docker-compose up"
echo ""
echo "  Start in background:"
echo "    docker-compose up -d"
echo ""
echo "  View logs:"
echo "    docker-compose logs -f"
echo ""
echo "  Stop container:"
echo "    docker-compose down"
echo ""
