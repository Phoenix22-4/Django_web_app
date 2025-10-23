# AquaGuard Railway Deployment Script (PowerShell)
# This script helps set up environment variables on Railway

Write-Host "🚀 AquaGuard Railway Deployment Setup" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if Railway CLI is installed
try {
    railway --version | Out-Null
    Write-Host "✅ Railway CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Railway CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g @railway/cli" -ForegroundColor Yellow
    Write-Host "   or visit: https://docs.railway.app/develop/cli" -ForegroundColor Yellow
    exit 1
}

# Login to Railway
Write-Host "🔐 Logging into Railway..." -ForegroundColor Blue
railway login

# Set environment variables
Write-Host "🔧 Setting up environment variables..." -ForegroundColor Blue

# Database Security
railway variables set DB_PASSWORD="+-1Ybs8Phot^#Mqv25HYhIzR&LliE5wT"

# Django Security
railway variables set SECRET_KEY="THQ#NIj)KJ5LYAbuMj)NVRrbR+mp$io5=IHjsZ5vCjf^MSpP_-"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="localhost,127.0.0.1,.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://localhost,https://127.0.0.1,https://.railway.app"

# Admin Security
railway variables set ADMIN_URL="AquaSavvy-Control/"

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green

# Deploy the application
Write-Host "🚀 Deploying to Railway..." -ForegroundColor Blue
railway up

Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Your admin panel is now at: https://your-app.railway.app/AquaSavvy-Control/" -ForegroundColor White
Write-Host "2. Monitor your application logs: railway logs" -ForegroundColor White
Write-Host "3. Check environment variables: railway variables" -ForegroundColor White
Write-Host ""
Write-Host "🔒 Security Features Active:" -ForegroundColor Cyan
Write-Host "- Custom admin URL: /AquaSavvy-Control/" -ForegroundColor White
Write-Host "- Rate limiting: 60 requests/minute" -ForegroundColor White
Write-Host "- CSRF protection on all endpoints" -ForegroundColor White
Write-Host "- Device ownership validation" -ForegroundColor White
Write-Host "- Comprehensive security logging" -ForegroundColor White
Write-Host ""
Write-Host "Support: contact@vision072025@gmail.com | WhatsApp: +254 702 715070" -ForegroundColor Yellow
