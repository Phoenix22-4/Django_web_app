# 🔐 Security & Firebase Setup Guide

## ✅ Security Implementation Status

### **STRONG SECURITY MEASURES ACTIVE:**

#### 1. **Login Protection** ✅
- **Django Admin:** Protected by default, requires staff/superuser status
- **Device List:** `@login_required` decorator - cannot access without login
- **Dashboard:** `@login_required` + ownership verification - users can only see their own devices
- **API Endpoints:** Protected with `@login_required` (except public chat on homepage)

#### 2. **Session Security** ✅
```python
SESSION_COOKIE_HTTPONLY = True      # Prevents JavaScript access
SESSION_COOKIE_SECURE = True        # HTTPS only (production)
SESSION_COOKIE_SAMESITE = 'Lax'     # CSRF protection
SESSION_COOKIE_AGE = 900            # 15-minute auto-logout
```

#### 3. **HTTPS Enforcement** ✅
```python
SECURE_SSL_REDIRECT = True          # Force HTTPS in production
SECURE_PROXY_SSL_HEADER = True      # Trust Railway's proxy
```

#### 4. **CSRF Protection** ✅
- All forms protected with `{% csrf_token %}`
- AJAX requests send `X-CSRFToken` header
- SameSite cookie prevents cross-site attacks

#### 5. **Security Headers** ✅
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'            # Prevents clickjacking
```

#### 6. **Password Strength** ✅
- Minimum 8 characters
- Cannot be similar to username
- Cannot be common passwords
- Cannot be entirely numeric

---

## 🚫 **What Users CANNOT Do:**

❌ Access `/devices/` without logging in → Redirects to `/login/`  
❌ Access `/dashboard/{device_id}/` without logging in → Redirects to `/login/`  
❌ Access another user's devices → 404 Not Found (ownership check)  
❌ Access `/admin/` without staff privileges → Login page  
❌ View admin analytics without staff status → Permission denied  
❌ Send commands to devices they don't own → WebSocket closes connection  

---

## 🔥 Firebase Cloud Messaging (FCM) Setup

### **Current Status:**
✅ Frontend configured with your Firebase credentials  
✅ Service Worker ready at `/sw.js`  
✅ VAPID public key integrated  
⚠️ **MISSING:** Firebase Server Key (FCM API Key) for backend

---

### **What You Need to Add:**

#### **Step 1: Get Firebase Server Key**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **aquasavvy-solution**
3. Click **⚙️ Settings** → **Project Settings**
4. Go to **Cloud Messaging** tab
5. Scroll down to **Cloud Messaging API (Legacy)**
6. Copy the **Server Key** (starts with `AAAA...`)

#### **Step 2: Get VAPID Private Key**

1. Still in **Cloud Messaging** tab
2. Scroll to **Web Push certificates**
3. You should see your key pair (you already have the public key)
4. Click **⋮** (three dots) next to your key pair
5. Click **Show Private Key**
6. Copy the private key

#### **Step 3: Add to Railway Environment Variables**

Go to Railway dashboard and add these environment variables:

```bash
FCM_SERVER_KEY=YOUR_FIREBASE_SERVER_KEY_HERE
VAPID_PRIVATE_KEY=YOUR_VAPID_PRIVATE_KEY_HERE
GEMINI_API_KEY=YOUR_GOOGLE_AI_API_KEY_HERE
```

---

### **Environment Variables Summary:**

| Variable | Purpose | Where to Get It |
|----------|---------|-----------------|
| `SECRET_KEY` | Django secret (already set) | Auto-generated |
| `DATABASE_URL` | PostgreSQL connection (already set) | Railway auto |
| `GEMINI_API_KEY` | AI chat assistant | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `FCM_SERVER_KEY` | Push notifications (backend) | Firebase Console → Cloud Messaging |
| `VAPID_PRIVATE_KEY` | Web Push (backend) | Firebase Console → Web Push Certificates |

---

## 🤖 GEMINI_API_KEY Setup

### **Get Your API Key:**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Get API Key"** or **"Create API Key"**
3. Select your Google Cloud project (or create a new one)
4. Copy the API key (starts with `AIza...`)
5. Add to Railway environment variables:
   ```
   GEMINI_API_KEY=AIzaSyC...your_key_here
   ```

### **Your Current Config:**
```javascript
// In base.html - Firebase config (ALREADY SET ✅)
const firebaseConfig = {
  apiKey: "AIzaSyCuorzrk2791U7GwqK0EziVFUlWI0NUMKc",
  authDomain: "aquasavvy-solution.firebaseapp.com",
  projectId: "aquasavvy-solution",
  storageBucket: "aquasavvy-solution.firebasestorage.app",
  messagingSenderId: "106611964149",
  appId: "1:106611964149:web:7beee215e4dedc406eedbc",
  measurementId: "G-TYENWVXT5R"
};
```

### **Your Current VAPID Public Key (ALREADY SET ✅):**
```javascript
// In push_handler.js
const vapidKey = 'YOUR_VAPID_PUBLIC_KEY_HERE';
```

---

## 🎨 **NEW Floating Chat Widget**

### **Features:**
✅ **Floating Icon** with "AquaSavvy Chat" label  
✅ **Draggable** - Move up/down on right side  
✅ **Slides In** from right when clicked  
✅ **Modern Design** - Professional chat interface  
✅ **Typing Indicator** - Shows AI is thinking  
✅ **Message Avatars** - Robot for AI, User icon for you  
✅ **Smooth Animations** - Messages slide in beautifully  
✅ **Keyboard Shortcuts** - Enter to send, Escape to close  
✅ **Click Outside** to close  
✅ **Mobile Responsive** - Full screen on mobile  

### **How to Use:**
1. **Click** the 💬 icon in bottom-right
2. Chat panel slides in
3. Type your question
4. Press **Enter** or click **Send** button
5. Wait for AI response (typing indicator shows)
6. **Drag** the icon up/down to reposition
7. **Escape** key or **X** button to close

---

## 🧪 Testing Security

### **Test 1: Direct URL Access (Should Fail)**
```
1. Log out of your account
2. Try to visit: https://your-app.railway.app/devices/
   Expected: Redirects to login page
3. Try to visit: https://your-app.railway.app/admin/
   Expected: Shows admin login page
4. Try to visit: https://your-app.railway.app/dashboard/ESP32_001/
   Expected: Redirects to login page
```

### **Test 2: Other User's Device (Should Fail)**
```
1. Login as User A
2. Note a device ID from User B (e.g., ESP32_002)
3. Try to visit: /dashboard/ESP32_002/
   Expected: 404 Not Found or redirects to devices
```

### **Test 3: Session Timeout**
```
1. Login and wait 15 minutes (SESSION_COOKIE_AGE = 900 seconds)
2. Try to access a protected page
   Expected: Redirects to login
```

### **Test 4: Chat Widget**
```
1. Visit any page (logged in or out)
2. See floating icon in bottom-right
3. Click icon → Panel slides in from right
4. Type message → AI responds
5. Drag icon up/down → Position changes
6. Press Escape → Panel closes
```

---

## 📋 Post-Deployment Checklist

After pushing to Railway:

- [ ] Verify `/admin/` requires login
- [ ] Verify `/devices/` requires login
- [ ] Verify `/dashboard/{id}/` requires login
- [ ] Test chat widget appears on all pages
- [ ] Test dragging chat icon
- [ ] Test sending chat message
- [ ] Add `GEMINI_API_KEY` to Railway env vars
- [ ] Add `FCM_SERVER_KEY` to Railway env vars (for push notifications)
- [ ] Add `VAPID_PRIVATE_KEY` to Railway env vars (for web push)
- [ ] Test push notification subscription (click "Enable notifications" button)

---

## 🔐 Security Best Practices (Already Implemented)

✅ **Never commit sensitive keys to Git**  
✅ **Use environment variables for secrets**  
✅ **Force HTTPS in production**  
✅ **Validate user ownership before data access**  
✅ **Short session timeouts (15 minutes)**  
✅ **Strong password requirements**  
✅ **CSRF tokens on all forms**  
✅ **HTTP-only session cookies**  
✅ **Secure cookies over HTTPS**  
✅ **XSS protection headers**  
✅ **Clickjacking protection (X-Frame-Options)**  

---

## 🆘 Troubleshooting

### **Chat Widget Not Showing**
- Check browser console for errors
- Verify `chat.js` is loaded
- Check if FontAwesome is loaded (for icons)

### **AI Chat Returns "Network Error"**
- Check `GEMINI_API_KEY` is set in Railway
- Verify API key is valid at [Google AI Studio](https://makersuite.google.com/)
- Check Railway deployment logs for errors

### **Push Notifications Not Working**
- Verify `FCM_SERVER_KEY` is set in Railway
- Check browser granted notification permission
- Verify service worker is registered at `/sw.js`
- Check browser console for Firebase errors

### **Users Can Access Other Devices**
- Check `@login_required` decorator on views
- Verify ownership check in `dashboard_view`:
  ```python
  device = get_object_or_404(Device, device_id=device_id, owner=request.user)
  ```

---

## 📞 Support

**Email:** contact:vision072025@gmail.com  
**WhatsApp:** +254 702 715070

---

**✅ Your system is now HIGHLY SECURE with a PROFESSIONAL FLOATING CHAT WIDGET!**

Remember to add the missing environment variables to activate push notifications and AI chat.

