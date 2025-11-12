#!/bin/bash
# Setup Redis on Railway using CLI
# 
# Prerequisites:
#   1. Install Railway CLI: npm i -g @railway/cli
#   2. Login: railway login
#   3. Link project: railway link (or railway init)
#
# Usage:
#   ./scripts/setup_redis_railway.sh

set -e

echo "🚂 Setting up Redis on Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install it with: npm i -g @railway/cli"
    exit 1
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Run: railway login"
    exit 1
fi

echo "✅ Railway CLI found and authenticated"

# Add Redis service
echo "📦 Adding Redis service to Railway project..."
railway add --database redis

echo "✅ Redis service added!"
echo ""
echo "📝 Next steps:"
echo "   1. Deploy your backend: railway up"
echo "   2. Redis connection will be available via REDIS_URL environment variable"
echo "   3. Your backend will automatically connect to Redis"
echo ""
echo "🔍 To verify Redis is connected, check your backend logs after deployment."

