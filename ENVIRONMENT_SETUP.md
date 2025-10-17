# Environment Variables Setup Guide

## Required Environment Variables for Railway Deployment

### 1. Django Settings
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app
```

### 2. Database (Railway provides automatically)
```bash
DATABASE_URL=postgresql://... (provided by Railway)
```

### 3. AWS IoT Configuration (Optional - for device communication)
```bash
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_IOT_ENDPOINT=your-iot-endpoint.amazonaws.com
```

### 4. Firebase Configuration (Optional - for push notifications)
```bash
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
```

### 5. Gemini AI Configuration (Optional - for AI chat)
```bash
GEMINI_API_KEY=your-gemini-api-key
```

## How to Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add each environment variable with its value
5. Click "Deploy" to apply changes

## Current Status

✅ **Working Features:**
- Basic web application
- User authentication
- Device management
- Dashboard interface
- Team member images
- Static files

⚠️ **Optional Features (require environment variables):**
- AWS IoT device communication
- Firebase push notifications
- Gemini AI chat assistance

## Notes

- The application will work without AWS IoT, Firebase, or Gemini API keys
- Missing credentials will show warnings in logs but won't break the application
- You can add these services later when needed
- All core functionality works without external services
