#!/bin/bash

# AquaGuard Railway Deployment Script
# This script helps set up environment variables on Railway

echo "🚀 AquaGuard Railway Deployment Setup"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Set environment variables
echo "🔧 Setting up environment variables..."

# Database Security
railway variables set DB_PASSWORD="+-1Ybs8Phot^#Mqv25HYhIzR&LliE5wT"

# Django Security
railway variables set SECRET_KEY="THQ#NIj)KJ5LYAbuMj)NVRrbR+mp$io5=IHjsZ5vCjf^MSpP_-"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="localhost,127.0.0.1,.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://localhost,https://127.0.0.1,https://.railway.app"

# Admin Security
railway variables set ADMIN_URL="AquaSavvy-Control/"

echo "✅ Environment variables set successfully!"

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "🎉 Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Your admin panel is now at: https://your-app.railway.app/AquaSavvy-Control/"
echo "2. Monitor your application logs: railway logs"
echo "3. Check environment variables: railway variables"
echo ""
echo "🔒 Security Features Active:"
echo "- Custom admin URL: /AquaSavvy-Control/"
echo "- Rate limiting: 60 requests/minute"
echo "- CSRF protection on all endpoints"
echo "- Device ownership validation"
echo "- Comprehensive security logging"
echo ""
echo "📞 Support: contact:vision072025@gmail.com | WhatsApp: +254 702 715070"
