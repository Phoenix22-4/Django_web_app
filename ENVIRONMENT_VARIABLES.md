# AquaGuard Environment Variables Configuration

## 🔒 CRITICAL SECURITY VARIABLES

**IMPORTANT**: Copy these variables to your Railway deployment environment variables section.

### Database Security
```
DB_PASSWORD=+-1Ybs8Phot^#Mqv25HYhIzR&LliE5wT
```

### Django Security
```
SECRET_KEY=THQ#NIj)KJ5LYAbuMj)NVRrbR+mp$io5=IHjsZ5vCjf^MSpP_-
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,.railway.app
CSRF_TRUSTED_ORIGINS=https://localhost,https://127.0.0.1,https://.railway.app
```

### Admin Security
```
ADMIN_URL=AquaSavvy-Control/
```

## 🚀 Railway Deployment Instructions

1. **Go to your Railway project dashboard**
2. **Click on "Variables" tab**
3. **Add each variable above one by one:**
   - Click "New Variable"
   - Enter the variable name (e.g., `DB_PASSWORD`)
   - Enter the variable value (e.g., `+-1Ybs8Phot^#Mqv25HYhIzR&LliE5wT`)
   - Click "Add"

4. **Required Variables to Add:**
   - `DB_PASSWORD`
   - `SECRET_KEY`
   - `DEBUG`
   - `ALLOWED_HOSTS`
   - `CSRF_TRUSTED_ORIGINS`
   - `ADMIN_URL`

## 🔧 Local Development

For local development, create a `.env` file in your project root with these variables.

## ⚠️ Security Notes

- These values are generated specifically for this project
- Never commit the `.env` file to version control
- Change these values if you suspect they've been compromised
- Use different values for production vs development

## 📞 Support

If you need help setting up environment variables:
- Email: contact:vision072025@gmail.com
- WhatsApp: +254 702 715070
