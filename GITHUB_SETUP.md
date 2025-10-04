# GitHub OAuth Setup Guide

## 🔧 Prerequisites for Full GitHub Integration

### 1. Create GitHub OAuth App

1. **Go to GitHub Developer Settings**:
   - Visit: https://github.com/settings/developers
   - Click "New OAuth App"

2. **Fill in the form**:
   ```
   Application name: Cookie-Licking Detector
   Homepage URL: http://localhost:5173
   Application description: AI-powered system to detect issue assignment abandonment
   Authorization callback URL: http://localhost:8002/api/auth/github/callback/
   ```

3. **Save and get credentials**:
   - Copy the `Client ID` (public)
   - Generate and copy the `Client Secret` (keep private)

### 2. Configure Environment Variables

Update the `.env` file in `backend2/` with your actual credentials:

```env
# Replace these with your actual GitHub OAuth app credentials
GITHUB_CLIENT_ID=your_actual_github_client_id_here
GITHUB_CLIENT_SECRET=your_actual_github_client_secret_here
```

### 3. Optional: Get Gemini AI API Key

For AI-powered trust scoring:

1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Current Status

- ✅ **Demo Mode**: Login works with simulated GitHub OAuth
- ✅ **Database**: User data is saved and retrieved
- ✅ **Frontend**: Complete login/logout flow
- ✅ **Backend**: All endpoints ready

## 🔄 What Works Now (Demo Mode)

1. **Login Flow**: Click "Continue with GitHub" → simulates OAuth → user created
2. **User Management**: Users saved in database with profiles
3. **Profile Display**: Shows username, avatar, trust score
4. **Admin Panel**: View all users at http://localhost:8002/admin/

## 🎯 What Happens With Real GitHub OAuth

Once you add real credentials:

1. **Real GitHub Login**: Users redirected to actual GitHub authorization
2. **Real User Data**: Fetches actual GitHub profile, repos, activity
3. **Trust Scoring**: AI analyzes real GitHub contributions
4. **Issue Tracking**: Monitors real repository issues and assignments

## 📋 Testing the Current Demo

1. Navigate to: http://localhost:5173/
2. Click "🔐 GitHub Login" tab
3. Click "Continue with GitHub"
4. See user created and logged in
5. Check admin panel to see saved user data

## 🔧 Next Steps

1. Create GitHub OAuth app (optional for demo)
2. Add real credentials to `.env`
3. Restart backend server
4. Test with real GitHub authentication

The system is fully functional in demo mode for testing all features!
