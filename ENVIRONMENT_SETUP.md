# Environment Variables Setup

## Required Environment Variables

### For Production (Railway/Heroku):
```bash
SECRET_KEY=n(7543fvi8l6$ymglo2+*9ge-dso$py5bi%zh89anhhm#0wa^i
DEBUG=False
RAILWAY_STATIC_URL=your-app-name.railway.app
```

### For Local Development:
```bash
SECRET_KEY=n(7543fvi8l6$ymglo2+*9ge-dso$py5bi%zh89anhhm#0wa^i
DEBUG=True
```

### Optional Variables:
```bash
# Database (if using external database)
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# AWS IoT Core
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_IOT_ENDPOINT=your_iot_endpoint

# Firebase Push Notifications
FIREBASE_SERVER_KEY=your_firebase_server_key

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

## How to Set Environment Variables

### On Railway:
1. Go to your Railway project dashboard
2. Click on "Variables" tab
3. Add the SECRET_KEY variable with the value above
4. Set DEBUG=False for production

### On Heroku:
```bash
heroku config:set SECRET_KEY="n(7543fvi8l6$ymglo2+*9ge-dso$py5bi%zh89anhhm#0wa^i"
heroku config:set DEBUG=False
```

### For Local Development:
Create a `.env` file in your project root:
```bash
SECRET_KEY=n(7543fvi8l6$ymglo2+*9ge-dso$py5bi%zh89anhhm#0wa^i
DEBUG=True
```

## Security Notes:
- Never commit the actual SECRET_KEY to version control
- Use different SECRET_KEYs for development and production
- The SECRET_KEY above is a secure, randomly generated key
- Keep your SECRET_KEY private and secure