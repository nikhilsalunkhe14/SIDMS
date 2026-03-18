# 🚀 SIDMS Vercel Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the SIDMS (Secure IAC Data Management System) to Vercel with a publicly accessible URL.

---

## 🔐 Step 1: Change Admin Password (Security Required)

**Before deploying, you MUST change the default admin credentials:**

### Method 1: Use the Automated Script (Recommended)

```bash
cd sidms-python-backend
python change_admin_password.py
```

Follow the prompts to set your new admin username and password.

### Method 2: Manual Change

Edit `sidms-python-backend/services/auth_service.py`:

```python
# Find these lines (around line 82):
if username == "iaccloudadmin" and password == "iaccloud@567":

# Replace with your new credentials:
if username == "YOUR_NEW_USERNAME" and password == "YOUR_NEW_PASSWORD":
```

Also update the admin user object (around line 86):
```python
'username': 'YOUR_NEW_USERNAME',
```

---

## 🌐 Step 2: Prepare Environment Variables

Create a `.env.production` file in the project root:

```env
# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sidms

# JWT Configuration  
JWT_SECRET_KEY=your-super-secret-jwt-key-here-min-32-chars
JWT_ACCESS_TOKEN_EXPIRES_IN=3600

# Encryption Configuration
ENCRYPTION_KEY=your-32-byte-encryption-key-here-very-secure

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Important:**
- Generate strong random keys for JWT_SECRET_KEY and ENCRYPTION_KEY
- Use your actual MongoDB Atlas connection string
- Never commit secrets to git

---

## 📦 Step 3: Install Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login
```

---

## 🚀 Step 4: Deploy to Vercel

### Option A: Automatic Deployment (Recommended)

```bash
# Navigate to project root
cd "e:\CYBER SECURITY - IP-11069\SIDMS-CODE-IP11069"

# Deploy with Vercel
vercel --prod

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your Vercel account
# - Link to existing project? No (first time)
# - Project name? sidms-secure-data-management
# - Directory? . (current directory)
```

### Option B: Manual Configuration

1. **Create Vercel Account**: [vercel.com](https://vercel.com)
2. **Connect GitHub**: Import your repository
3. **Configure Settings**:
   - **Build Command**: `npm run build`
   - **Output Directory**: `sidms-frontend/dist`
   - **Install Command**: `npm install`
   - **Node Version**: 18.x

---

## ⚙️ Step 5: Configure Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings → Environment Variables**
3. Add all variables from your `.env.production` file:

| Variable | Value |
|----------|-------|
| `MONGODB_URI` | Your MongoDB connection string |
| `JWT_SECRET_KEY` | Your JWT secret key |
| `JWT_ACCESS_TOKEN_EXPIRES_IN` | 3600 |
| `ENCRYPTION_KEY` | Your 32-byte encryption key |
| `SMTP_SERVER` | smtp.gmail.com (optional) |
| `SMTP_PORT` | 587 (optional) |
| `SMTP_USERNAME` | Your email (optional) |
| `SMTP_PASSWORD` | Your app password (optional) |

---

## 🔄 Step 6: Update Frontend API Configuration

Edit `sidms-frontend/src/utils/apiClient.js`:

```javascript
// For production deployment
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Vercel serverless function
  : 'http://localhost:5000';  // Local development
```

---

## 🎯 Step 7: Deploy and Test

### Final Deployment

```bash
# Deploy to production
vercel --prod

# Your app will be available at: https://your-project-name.vercel.app
```

### Testing Checklist

- [ ] **Backend API**: Test `https://your-app.vercel.app/api/health`
- [ ] **Frontend**: Access `https://your-app.vercel.app`
- [ ] **Admin Login**: Use your new admin credentials
- [ ] **Database Connection**: Verify MongoDB Atlas connection
- [ ] **Encryption**: Test profile creation and data encryption
- [ ] **MFA**: Test multi-factor authentication setup

---

## 🔧 Troubleshooting

### Common Issues

#### ❌ "Function Not Found" Error
```bash
# Ensure the api/index.py file exists in the correct location
sidms-python-backend/api/index.py
```

#### ❌ "Database Connection Failed"
- Verify MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Check connection string format
- Ensure database user has proper permissions

#### ❌ "Environment Variables Not Working"
- Double-check variable names in Vercel dashboard
- Ensure no trailing spaces in values
- Verify sensitive data is properly escaped

#### ❌ "CORS Errors"
- Check Vercel configuration in `vercel.json`
- Ensure API routes are properly configured
- Verify frontend is calling correct API endpoints

### Debug Commands

```bash
# Check deployment logs
vercel logs

# Check environment variables
vercel env ls

# Redeploy with latest changes
vercel --prod --force
```

---

## 🛡️ Security Considerations

### Production Security Checklist

- [ ] **Admin password changed** from default
- [ ] **Strong JWT secret key** (32+ characters)
- [ ] **Strong encryption key** (32 bytes)
- [ ] **HTTPS enabled** (automatic with Vercel)
- [ ] **MongoDB Atlas security** configured
- [ ] **Environment variables** set in Vercel
- [ ] **No hardcoded secrets** in code
- [ ] **CORS properly configured**
- [ ] **Security headers** implemented

### Monitoring and Maintenance

- Monitor Vercel logs for errors
- Regularly rotate encryption keys
- Keep dependencies updated
- Monitor MongoDB Atlas usage
- Set up alerts for security events

---

## 📱 Access Your Deployed Application

After successful deployment:

1. **Main Application**: `https://your-project-name.vercel.app`
2. **API Health Check**: `https://your-project-name.vercel.app/api/health`
3. **Admin Dashboard**: Login with your new admin credentials

---

## 🔄 Updating Your Application

### Making Changes

1. **Update code** in your local repository
2. **Test locally** to ensure everything works
3. **Deploy updates**:
   ```bash
   vercel --prod
   ```
4. **Verify deployment** through the Vercel dashboard

### Database Changes

- For schema changes, update MongoDB Atlas directly
- For configuration changes, update environment variables in Vercel
- Always test changes in development first

---

## 📞 Support

### Vercel Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

### Project Documentation
- `README.md` - Complete project overview
- `CODING_STANDARDS.md` - Development guidelines
- `SETUP_GUIDE.md` - Local setup instructions

---

## 🎉 Success!

Your SIDMS application is now deployed and accessible via a public URL! The system includes:

- ✅ **Secure Authentication** with your custom admin credentials
- ✅ **AES-256 Encryption** for sensitive data
- ✅ **Multi-Factor Authentication** support
- ✅ **GDPR Compliance** features
- ✅ **Comprehensive Audit Trail**
- ✅ **HTTPS Security** (automatic with Vercel)

**Remember to keep your admin credentials secure and monitor your application regularly!**
