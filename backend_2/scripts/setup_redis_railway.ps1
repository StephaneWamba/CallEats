# Setup Redis on Railway using CLI (PowerShell)
# 
# Prerequisites:
#   1. Install Railway CLI: npm i -g @railway/cli
#   2. Login: railway login
#   3. Link project: railway link (or railway init)
#
# Usage:
#   .\scripts\setup_redis_railway.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚂 Setting up Redis on Railway..." -ForegroundColor Cyan

# Check if Railway CLI is installed
try {
    $null = Get-Command railway -ErrorAction Stop
}
catch {
    Write-Host "❌ Railway CLI not found. Install it with: npm i -g @railway/cli" -ForegroundColor Red
    exit 1
}

# Check if logged in
try {
    $null = railway whoami 2>&1
}
catch {
    Write-Host "❌ Not logged in to Railway. Run: railway login" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Railway CLI found and authenticated" -ForegroundColor Green

# Add Redis service
Write-Host "📦 Adding Redis service to Railway project..." -ForegroundColor Cyan
railway add --database redis

Write-Host "✅ Redis service added!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Deploy your backend: railway up"
Write-Host "   2. Redis connection will be available via REDIS_URL environment variable"
Write-Host "   3. Your backend will automatically connect to Redis"
Write-Host ""
Write-Host "🔍 To verify Redis is connected, check your backend logs after deployment." -ForegroundColor Cyan

