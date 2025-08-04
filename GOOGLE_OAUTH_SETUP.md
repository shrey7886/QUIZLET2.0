# 🔐 Google OAuth Setup Guide

## 📋 **Prerequisites**
- Google Cloud Console account
- Your Quizlet app running locally

## 🚀 **Step-by-Step Setup**

### **Step 1: Create Google Cloud Project**

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select existing one
3. **Enable Google+ API** (if not already enabled)

### **Step 2: Configure OAuth Consent Screen**

1. **Go to "APIs & Services" → "OAuth consent screen"**
2. **Choose "External"** (for development)
3. **Fill in required information:**
   - App name: `Quizlet AI Quiz Generator`
   - User support email: Your email
   - Developer contact information: Your email
4. **Add scopes:**
   - `email`
   - `profile`
5. **Add test users** (your email addresses)

### **Step 3: Create OAuth 2.0 Credentials**

1. **Go to "APIs & Services" → "Credentials"**
2. **Click "Create Credentials" → "OAuth 2.0 Client IDs"**
3. **Choose "Web application"**
4. **Configure:**
   - Name: `Quizlet AI Web Client`
   - Authorized JavaScript origins:
     ```
     http://localhost:8000
     http://localhost:3000
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:8000/api/auth/google/callback
     http://localhost:8000/auth/callback
     ```

### **Step 4: Get Your Credentials**

1. **Copy the Client ID and Client Secret**
2. **Add them to your `.env` file:**

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

### **Step 5: Update Frontend Configuration**

1. **Open `frontend/src/components/LoginForm.tsx`**
2. **Replace `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID:**

```typescript
client_id: 'your-actual-google-client-id-here',
```

### **Step 6: Test the Integration**

1. **Start your backend server:**
   ```bash
   python main.py
   ```

2. **Start your frontend (if separate):**
   ```bash
   cd frontend
   npm start
   ```

3. **Go to `http://localhost:8000/login`**
4. **Click "Continue with Google"**
5. **Complete the OAuth flow**

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Invalid redirect URI"**
   - Check that your redirect URI exactly matches what's in Google Console
   - Make sure there are no trailing slashes

2. **"Client ID not found"**
   - Verify your Client ID is correct
   - Make sure you're using the Web application client, not Android/iOS

3. **"OAuth consent screen not configured"**
   - Complete the OAuth consent screen setup
   - Add your email as a test user

4. **"Redirect URI mismatch"**
   - Check that the redirect URI in your code matches Google Console
   - For localhost, use `http://localhost:8000/api/auth/google/callback`

## 🚀 **Production Deployment**

When deploying to production:

1. **Update redirect URIs in Google Console:**
   ```
   https://your-domain.com/api/auth/google/callback
   https://your-domain.com/auth/callback
   ```

2. **Update JavaScript origins:**
   ```
   https://your-domain.com
   ```

3. **Set environment variables on your hosting platform**

## 📝 **Security Notes**

- **Never commit your Client Secret to version control**
- **Use environment variables for all sensitive data**
- **Enable HTTPS in production**
- **Regularly rotate your credentials**

## 🎉 **You're Ready!**

Once configured, users can sign in with their Google accounts seamlessly! 