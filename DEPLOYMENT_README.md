# 🚀 Streamlit Cloud Deployment Guide

## Interactive Intake Chatbot System

This guide will help you deploy the Interactive Intake Chatbot System to Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **OpenAI API Key** - Get one from [OpenAI](https://platform.openai.com/api-keys)

## 🔧 Deployment Steps

### 1. Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Interactive Intake Chatbot"
   git branch -M main
   git remote add origin https://github.com/yourusername/intake-chatbot.git
   git push -u origin main
   ```

### 2. Deploy on Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Click "New app"**
3. **Connect your GitHub repository**
4. **Configure the app**:
   - **Repository**: `yourusername/intake-chatbot`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom URL

### 3. Configure Secrets

1. **In your Streamlit Cloud app dashboard, go to "Settings" → "Secrets"**
2. **Add your OpenAI API key**:
   ```toml
   OPENAI_API_KEY = "your-actual-openai-api-key-here"
   ```
3. **Click "Save"**

### 4. Deploy

1. **Click "Deploy!"**
2. **Wait for the app to build and deploy** (usually takes 2-5 minutes)
3. **Your app will be live at**: `https://your-app-name.streamlit.app`

## 🎯 Features Available in Deployment

✅ **Full Authentication System**
- Business-specific login (4 organizations included)
- Role-based access control

✅ **Interactive Chatbot**
- GPT-4o mini powered conversations
- Formal/Informal communication modes
- Smart validation and help responses

✅ **Admin Portal**
- Form template management with versioning
- Submitted application viewing
- Export functionality (CSV/JSON)

✅ **Client Interface**
- Conversational intake forms
- Progress tracking
- Radio button selections for categorical questions

## 🔐 Security Features

- ✅ OpenAI API key stored securely in Streamlit secrets
- ✅ Organization-based data isolation
- ✅ Session-based authentication
- ✅ No hardcoded credentials in public code

## 📝 Sample Login Credentials

**For testing purposes, use these credentials:**

| Organization | Username | Password |
|-------------|----------|----------|
| Broomfield Department of Health | broomfield_admin | 123456 |
| First Things First | ftf_admin | 123456 |
| Gateway YMCA | gateway_admin | 123456 |
| SBNJ Mobile Midwife Clinic | sbnj_admin | 123456 |

## 🛠️ Troubleshooting

### Common Issues:

1. **"OPENAI_API_KEY not found" error**:
   - Ensure you've added the API key to Streamlit secrets
   - Check for typos in the secret key name

2. **Import errors**:
   - Verify all dependencies are in `requirements.txt`
   - Check Python version compatibility

3. **File permission errors**:
   - All necessary directories are created automatically
   - Cloud deployment handles file system permissions

### Debug Mode:

The app includes debug logging. Check the Streamlit Cloud logs if you encounter issues.

## 📱 Usage After Deployment

1. **Access your deployed app** at the provided URL
2. **Choose login type**: Client or Admin
3. **Use sample credentials** or create your own
4. **Test all features**:
   - Submit intake forms as clients
   - Review applications as admins
   - Try both formal and informal communication modes

## 🔄 Updates

To update your deployed app:
1. **Push changes to your GitHub repository**
2. **Streamlit Cloud will automatically redeploy**
3. **No manual intervention needed**

## 📞 Support

If you encounter issues during deployment:
1. Check Streamlit Cloud documentation
2. Review the app logs in the Streamlit Cloud dashboard
3. Ensure all secrets are properly configured

---

🎉 **Your Interactive Intake Chatbot is now live on Streamlit Cloud!**
