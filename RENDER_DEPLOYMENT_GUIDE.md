# 🚀 SIDMS Render Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the SIDMS (Secure IAC Data Management System) to Render with a publicly accessible URL.

---

## 🔐 Step 1: Change Admin Password (Security Required)

**Before deploying, you MUST change the default admin credentials:**

### Run the Password Change Script
```bash
cd sidms-python-backend
python change_admin_password.py
```

Follow the prompts to set your new admin username and password.

---

## 🌐 Step 2: Prepare for Render Deployment

### Prerequisites
- **Render Account**: [render.com](https://render.com)
- **GitHub Account**: For repository connection
- **MongoDB Atlas**: Database setup

### Project Structure
Your project is already configured with:
- `render.yaml` - Render service configuration
- Frontend and backend services defined
- Environment variables ready

---

## 🚀 Step 3: Deploy to Render

### Option A: GitHub Repository (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for Render deployment"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the SIDMS repository
   - Render will auto-detect the `render.yaml` configuration

### Option B: Manual Deployment

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Choose "Build and deploy from a Git repository"

2. **Configure Frontend Service**:
   - **Name**: `sidms-frontend`
   - **Environment**: `Node`
   - **Build Command**: `cd sidms-frontend && npm install && npm run build`
   - **Start Command**: `cd sidms-frontend && npm start`
   - **Publish Directory**: `./sidms-frontend/dist`

3. **Configure Backend Service**:
   - **Name**: `sidms-backend`
   - **Environment**: `Python`
   - **Build Command**: `cd sidms-python-backend && pip install -r requirements-vercel.txt`
   - **Start Command**: `cd sidms-python-backend && python app.py`

---

## ⚙️ Step 4: Configure Environment Variables

### Frontend Environment Variables
In your frontend service settings:
```env
REACT_APP_API_URL=https://your-backend-url.onrender.com/api
```

### Backend Environment Variables
In your backend service settings:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sidms
JWT_SECRET_KEY=your-super-secret-jwt-key-here-min-32-chars
JWT_ACCESS_TOKEN_EXPIRES_IN=3600
ENCRYPTION_KEY=your-32-byte-encryption-key-here-very-secure
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🔧 Step 5: Update Frontend API Configuration

Edit `sidms-frontend/src/utils/apiClient.js`:

```javascript
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? process.env.REACT_APP_API_URL || 'https://your-backend-url.onrender.com/api'
  : 'http://localhost:5000';  // Local development
```

---

## 🌐 Step 6: Access Your Deployed Application

After deployment, you'll have two URLs:

### Frontend URL
```
https://sidms-frontend.onrender.com
```

### Backend API URL
```
https://sidms-backend.onrender.com/api
```

### Health Check
```bash
curl https://sidms-backend.onrender.com/health
```

---

## 🔍 Testing Your Deployment

### 1. Test Backend
- Open: `https://sidms-backend.onrender.com/health`
- Should return: `{"status": "healthy", "message": "SIDMS Backend is running"}`

### 2. Test Frontend
- Open: `https://sidms-frontend.onrender.com`
- Should see the login page
- Try logging in with your new admin credentials

### 3. Test Full Application
- Create user profiles
- Test encryption features
- Verify MFA setup
- Check audit logs

---

## 🛠️ Troubleshooting

### Common Issues

#### ❌ "Build Failed"
- Check `package.json` for correct scripts
- Verify `requirements-vercel.txt` exists
- Check for syntax errors in configuration

#### ❌ "Application Not Responding"
- Verify start commands are correct
- Check health check paths
- Review build logs in Render dashboard

#### ❌ "API Connection Failed"
- Update `REACT_APP_API_URL` environment variable
- Check CORS configuration in backend
- Verify backend is running

#### ❌ "Database Connection Failed"
- Verify MongoDB URI is correct
- Check IP whitelist in MongoDB Atlas
- Ensure database user has proper permissions

### Debug Commands

```bash
# Check frontend build locally
cd sidms-frontend
npm run build

# Check backend locally
cd sidms-python-backend
python app.py

# Test API locally
curl http://localhost:5000/health
```

---

## 🔄 Updating Your Application

### Making Changes
1. **Update code** in your local repository
2. **Test locally** to ensure everything works
3. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
4. **Render will auto-deploy** your changes

### Database Changes
- For schema changes, update MongoDB Atlas directly
- For configuration changes, update environment variables in Render
- Always test changes in development first

---

## 📱 Render-Specific Features

### Auto-Deploy
- Render automatically deploys when you push to GitHub
- No manual deployment needed after initial setup
- Builds are cached for faster deployments

### Custom Domains
- Add custom domains in Render dashboard
- Free SSL certificates included
- Automatic HTTPS redirection

### Monitoring
- Built-in metrics and logs
- Error tracking
- Performance monitoring

---

## 🛡️ Security Considerations for Production

### Critical Security Checklist
- [ ] **Admin password changed** from default
- [ ] **Strong JWT secret key** (32+ characters)
- [ ] **Strong encryption key** (32 bytes)
- [ ] **Environment variables** set in Render
- [ ] **MongoDB Atlas security** configured
- [ ] **HTTPS enabled** (automatic with Render)
- [ ] **No hardcoded secrets** in code
- [ ] **CORS properly configured**

### Monitoring and Maintenance
- Monitor Render logs for errors
- Regularly rotate encryption keys
- Keep dependencies updated
- Monitor MongoDB Atlas usage
- Set up alerts for security events

---

## 📊 Comparison: Render vs Vercel

| Feature | Render | Vercel |
|----------|---------|---------|
| **Backend Support** | ✅ Native Python/Node | ⚠️ Serverless only |
| **Database** | ✅ Direct connection | ✅ Direct connection |
| **Free Tier** | ✅ 750 hours/month | ✅ Limited |
| **Custom Domains** | ✅ Free SSL | ✅ Free SSL |
| **Auto-Deploy** | ✅ GitHub integration | ✅ GitHub integration |
| **Monitoring** | ✅ Built-in | ✅ Built-in |

---

## 🎉 Success!

Your SIDMS application is now deployed on Render with:

- ✅ **Secure Authentication** with your custom admin credentials
- ✅ **AES-256 Encryption** for sensitive data
- ✅ **Multi-Factor Authentication** support
- ✅ **GDPR Compliance** features
- ✅ **Comprehensive Audit Trail**
- ✅ **HTTPS Security** (automatic with Render)
- ✅ **Auto-Deploy** from GitHub

---

## 📞 Support Resources

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Environment Variables](https://render.com/docs/env-vars)
- [Web Services](https://render.com/docs/web-services)

### Project Documentation
- `README.md` - Complete project overview
- `CODING_STANDARDS.md` - Development guidelines
- `ADMIN_PASSWORD_CHANGE_GUIDE.md` - Password security

---

**Document Version:** 1.0  
**Last Updated:** 2025  
**Project:** SIDMS - Secure IAC Data Management System  
**Platform:** Render
