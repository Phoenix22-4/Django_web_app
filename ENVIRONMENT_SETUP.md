# Environment Variables Setup Guide

## Required Environment Variables for Railway

### AWS IoT Credentials (For Device Control)
```
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
AWS_IOT_ENDPOINT=your-iot-endpoint.amazonaws.com
```

### Gemini AI (For Chat Assistant)
```
GEMINI_API_KEY=your-gemini-api-key
```

### Firebase (For Push Notifications - Optional)
```
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id",...}
```

## How to Set Environment Variables in Railway

1. Go to [railway.app](https://railway.app)
2. Sign in and select your AquaGuard project
3. Click on your Django service
4. Go to the **"Variables"** tab
5. Click **"New Variable"** for each environment variable
6. Add the variable name and value
7. Click **"Deploy"** to apply changes

## How to Get Firebase Service Account JSON

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **"Generate new private key"**
5. Download the JSON file
6. Copy the entire JSON content as the value for `FIREBASE_SERVICE_ACCOUNT_JSON`

## What Works Without Credentials

- ✅ Basic web application
- ✅ User authentication
- ✅ Dashboard interface
- ✅ Static files and CSS
- ✅ Database operations

## What Needs Credentials

- ⚠️ AWS IoT device communication
- ⚠️ Gemini AI chat assistant
- ⚠️ Firebase push notifications

## Security Notes

- **Never commit credentials to Git**
- **Use Railway's environment variables** for secure storage
- **Rotate credentials regularly**
- **Use IAM roles with minimal permissions**

## After Setup

Once you add the environment variables and deploy:
1. **AWS IoT** will work for device control
2. **Gemini AI** will work for chat assistance
3. **Firebase** will work for push notifications
4. **All features** will be fully functional