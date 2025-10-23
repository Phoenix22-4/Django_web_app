# AquaGuard Security Configuration Guide

## 🔒 CRITICAL SECURITY REQUIREMENTS

This document outlines the **MANDATORY** security configuration for the AquaGuard Django application. **ALL** of these settings must be properly configured before deployment.

## Environment Variables (REQUIRED)

### Database Security
```bash
# REQUIRED: Database password (NEVER hardcode in settings.py)
DB_PASSWORD=your_secure_database_password_here

# REQUIRED: Database URL for production
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Django Security
```bash
# REQUIRED: Django secret key (generate new one for production)
SECRET_KEY=your-very-long-random-secret-key-here

# REQUIRED: Debug mode (MUST be False in production)
DEBUG=False

# REQUIRED: Allowed hosts for production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# REQUIRED: CSRF trusted origins
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Admin Security
```bash
# REQUIRED: Custom admin URL (change from default /admin/)
ADMIN_URL=AquaSavvy-Control/
```

### API Keys
```bash
# OPTIONAL: Gemini AI API key
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL: Firebase credentials
FIREBASE_SERVICE_ACCOUNT_JSON=your_firebase_credentials_json_here

# OPTIONAL: Redis URL for production
REDIS_URL=redis://username:password@host:port/database
```

## Security Features Implemented

### ✅ OWASP Top 10 Mitigation

1. **Injection Prevention**
   - Parameterized queries using Django ORM
   - Input validation on all API endpoints
   - SQL injection protection via Django's built-in protections

2. **Broken Authentication**
   - Rate limiting on login attempts (5 attempts per 5 minutes)
   - Strong password requirements (12+ characters)
   - Session security with HttpOnly cookies
   - Custom admin URL to prevent automated attacks

3. **Sensitive Data Exposure**
   - All secrets stored in environment variables
   - Database credentials never hardcoded
   - Secure session configuration
   - HTTPS enforcement in production

4. **XML External Entities (XXE)**
   - Not applicable (no XML processing)

5. **Broken Access Control**
   - Device ownership validation on all operations
   - User authentication required for all sensitive endpoints
   - Proper authorization checks in views

6. **Security Misconfiguration**
   - Custom admin URL implemented
   - Security headers configured
   - Debug mode disabled in production
   - Secure cookie settings

7. **Cross-Site Scripting (XSS)**
   - Template auto-escaping enabled
   - Manual escaping for JavaScript data
   - Content Security Policy implemented
   - Input sanitization on all user inputs

8. **Insecure Deserialization**
   - JSON validation on all API inputs
   - Type checking for all parameters
   - No pickle or unsafe deserialization

9. **Using Components with Known Vulnerabilities**
   - Regular dependency updates recommended
   - Security-focused package selection

10. **Insufficient Logging & Monitoring**
    - Comprehensive security event logging
    - Failed login attempt monitoring
    - Admin access logging
    - Rate limiting with logging

### 🔐 Enhanced Security Features

#### Rate Limiting
- **General API**: 60 requests per minute per IP
- **Login attempts**: 5 attempts per 5 minutes per IP
- **AI Chat**: 20 requests per minute per user
- **Device control**: 20 requests per minute per user

#### Input Validation
- **JSON validation**: All API endpoints validate JSON structure
- **Type checking**: String, integer, boolean validation
- **Length limits**: Maximum 1000 characters for strings
- **XSS prevention**: Dangerous HTML tags blocked
- **Device ID validation**: Alphanumeric with hyphens/underscores only

#### Authentication & Authorization
- **Device ownership**: Users can only access their own devices
- **Superuser override**: Admins can access all devices
- **Session security**: 30-minute timeout, HttpOnly cookies
- **CSRF protection**: All forms and API endpoints protected

#### Security Headers
- **Content Security Policy**: Restricts resource loading
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **Strict-Transport-Security**: HTTPS enforcement
- **Referrer-Policy**: Controls referrer information

## Deployment Checklist

### Before Deployment
- [ ] Set `DEBUG=False`
- [ ] Configure `SECRET_KEY` environment variable
- [ ] Set `DB_PASSWORD` environment variable
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Set `CSRF_TRUSTED_ORIGINS` for your domain
- [ ] Change admin URL from default
- [ ] Enable HTTPS in production
- [ ] Configure Redis for production (if using)

### After Deployment
- [ ] Test admin access at custom URL
- [ ] Verify HTTPS redirect works
- [ ] Test rate limiting functionality
- [ ] Verify security headers are present
- [ ] Test device ownership restrictions
- [ ] Monitor security logs

## Security Monitoring

### Log Events to Monitor
- Failed login attempts
- Rate limit violations
- Admin access
- Device access violations
- CSRF failures
- Suspicious API usage

### Recommended Monitoring Tools
- Django logging to file
- External monitoring service
- Database query monitoring
- Network traffic analysis

## Emergency Response

### If Security Breach Suspected
1. **Immediate Actions**:
   - Change all passwords
   - Rotate SECRET_KEY
   - Review access logs
   - Check for unauthorized device access

2. **Investigation**:
   - Analyze security logs
   - Check database for anomalies
   - Review user accounts
   - Verify device configurations

3. **Recovery**:
   - Update all dependencies
   - Review and strengthen security measures
   - Implement additional monitoring
   - Notify affected users if necessary

## Contact Information

For security issues or questions:
- **Email**: contact:vision072025@gmail.com
- **WhatsApp**: +254 702 715070

**NEVER** report security vulnerabilities through public channels. Use the contact information above for responsible disclosure.
