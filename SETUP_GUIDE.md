# 🚀 SIDMS Setup Guide for Managers

## 📋 Overview

This guide provides step-by-step instructions for setting up and running the **SIDMS (Secure IAC Data Management System)** on your local machine. The system includes enterprise-grade security features like AES-256 encryption, multi-factor authentication, and GDPR compliance.

---

## 🎯 Quick Start Summary

| Step | Action | Time Required | Difficulty |
|------|--------|---------------|------------|
| 1 | Install Prerequisites | 15-30 minutes | Easy |
| 2 | Download & Extract Project | 5 minutes | Easy |
| 3 | Configure Environment | 10 minutes | Medium |
| 4 | Set up Database | 10 minutes | Medium |
| 5 | Run Applications | 5 minutes | Easy |
| **Total** | **Complete Setup** | **45-60 minutes** | **Medium** |

---

## 🔧 Prerequisites Installation

### 1. Python 3.10+ (Required)

**Windows:**
1. Download Python from [python.org](https://python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Verify installation:
   ```cmd
   python --version
   ```

**macOS:**
```bash
# Install using Homebrew
brew install python@3.10

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### 2. Node.js 18+ (Required)

**Download from:** [nodejs.org](https://nodejs.org/)

**Verify installation:**
```cmd
node --version
npm --version
```

### 3. MongoDB Atlas Account (Required)

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Choose **Free Plan** (M0 Sandbox)
3. Create a cluster (takes 2-5 minutes)
4. Get your connection string

### 4. Git (Recommended)

**Download from:** [git-scm.com](https://git-scm.com/downloads)

---

## 📦 Project Setup Instructions

### Step 1: Download and Extract Project

1. **Download** the SIDMS project ZIP file
2. **Extract** to your preferred location (e.g., `C:\SIDMS`)
3. **Navigate** to the project directory:
   ```cmd
   cd C:\SIDMS
   ```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

**Windows:**
```cmd
cd sidms-python-backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd sidms-python-backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```cmd
pip install Flask Flask-CORS PyJWT pymongo python-dotenv pyotp qrcode[pil] cryptography bcrypt
```

#### 2.3 Create Environment File

Create a new file named `.env` in `sidms-python-backend/`:

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

**🔑 Important Security Notes:**
- Replace `username:password` with your MongoDB Atlas credentials
- Generate strong random keys for JWT_SECRET_KEY and ENCRYPTION_KEY
- For Gmail, use an **App Password** (not your regular password)

### Step 3: Frontend Setup

#### 3.1 Install Node.js Dependencies

```cmd
cd sidms-frontend
npm install
```

#### 3.2 Configure API URL (if needed)

The frontend is configured to connect to `http://localhost:5000` by default. If you need to change this:

Edit `src/utils/apiClient.js`:
```javascript
const BASE_URL = 'http://localhost:5000'; // Change if needed
```

---

## 🗄️ Database Configuration

### MongoDB Atlas Setup

1. **Create Database:**
   - Go to your MongoDB Atlas dashboard
   - Navigate to "Collections"
   - Click "Create Database"
   - Name: `sidms`

2. **Network Access:**
   - Go to "Network Access"
   - Add IP: `0.0.0.0/0` (allows access from anywhere)

3. **Get Connection String:**
   - Go to "Database" → "Connect"
   - Select "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

### Test Database Connection

```cmd
cd sidms-python-backend
python -c "
from config.database import db_instance
try:
    db_instance.test_connection()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

---

## 🚀 Running the Applications

### Step 1: Start Backend Server

```cmd
cd sidms-python-backend
# Make sure virtual environment is activated
python app.py
```

**Expected Output:**
```
✅ Connected to MongoDB Atlas successfully!
✅ Database connected successfully
🌐 Starting SIDMS Backend on HTTP...
🌍 HTTP URL: http://localhost:5000
* Running on http://127.0.0.1:5000
```

### Step 2: Start Frontend Server

**Open a NEW terminal window:**

```cmd
cd sidms-frontend
npm run dev
```

**Expected Output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h to show help
```

---

## 🔐 Default Login Credentials

### Admin Account
- **Username:** `iaccloudadmin`
- **Password:** `iaccloud@567`

### First-Time Setup

1. **Open browser:** Navigate to `http://localhost:5173`
2. **Login** with admin credentials
3. **Enable MFA** (recommended for security)
4. **Create test profiles** to verify encryption works

---

## 🛡️ Security Features Verification

### Test AES-256 Encryption

1. Create a new member profile
2. Fill in sensitive data (name, email, phone)
3. Check the data is encrypted in MongoDB Atlas
4. Verify data decrypts correctly when viewed

### Test Multi-Factor Authentication

1. Go to user settings
2. Set up MFA with QR code
3. Use Google Authenticator app
4. Test login with MFA

### Test GDPR Compliance

1. Export user data (GDPR right to access)
2. Test data deletion (right to be forgotten)
3. Check compliance reports

---

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### ❌ "Python command not found"
**Solution:** 
- Ensure Python is added to PATH during installation
- Use `python3` instead of `python` on macOS/Linux

#### ❌ "Virtual environment activation failed"
**Solution:**
```cmd
# Windows - Run as Administrator
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### ❌ "MongoDB connection failed"
**Solution:**
1. Verify IP address is whitelisted in MongoDB Atlas
2. Check username/password in connection string
3. Ensure database user has proper permissions

#### ❌ "Port already in use"
**Solution:**
```cmd
# Find process using port
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

#### ❌ "Frontend not connecting to backend"
**Solution:**
1. Ensure backend is running on port 5000
2. Check CORS configuration in backend
3. Verify API URL in frontend configuration

#### ❌ "Encryption key errors"
**Solution:**
1. Generate a new 32-byte key:
   ```cmd
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Update ENCRYPTION_KEY in .env file
3. Restart backend server

---

## 📱 Mobile Setup (Optional)

### For Testing on Mobile Devices

1. **Find your local IP:**
   ```cmd
   ipconfig
   ```
2. **Update frontend API URL:**
   - Edit `src/utils/apiClient.js`
   - Replace `localhost` with your IP address
3. **Connect devices to same WiFi network**
4. **Access frontend:** `http://YOUR_IP:5173`

---

## 🚀 Production Deployment Notes

### Security Considerations

1. **Change all default passwords**
2. **Use environment-specific secrets**
3. **Enable HTTPS/SSL in production**
4. **Set up proper firewall rules**
5. **Enable MongoDB Atlas security features**
6. **Regular security audits**

### Performance Optimization

1. **Use production WSGI server** (Gunicorn)
2. **Enable MongoDB indexing**
3. **Implement caching**
4. **Set up monitoring and logging**

---

## 📞 Support & Resources

### Documentation
- **README.md:** Complete project overview
- **compliance/GDPR_COMPLIANCE.md:** GDPR documentation
- **API Endpoints:** Full API documentation in README

### Quick Commands Reference

```cmd
# Backend
cd sidms-python-backend
venv\Scripts\activate
python app.py

# Frontend
cd sidms-frontend
npm run dev

# Database Test
python -c "from config.database import db_instance; print('DB OK')"

# Generate Keys
python -c "import secrets; print('JWT:', secrets.token_urlsafe(32)); print('ENC:', secrets.token_urlsafe(32))"
```

### Environment Variables Template

```env
# Copy this template and fill in your values
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sidms
JWT_SECRET_KEY=your-jwt-secret-key-32-chars-minimum
JWT_ACCESS_TOKEN_EXPIRES_IN=3600
ENCRYPTION_KEY=your-32-byte-encryption-key-here-very-secure
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🎉 Success Checklist

### ✅ Verify Everything Works

- [ ] **Backend starts** on http://localhost:5000
- [ ] **Frontend starts** on http://localhost:5173
- [ ] **Database connects** successfully
- [ ] **Admin login** works
- [ ] **Profile creation** works
- [ ] **Data encryption** verified
- [ ] **MFA setup** works
- [ ] **Compliance features** accessible

### 🏆 Ready to Use!

Once all checkboxes are checked, your SIDMS system is fully operational with enterprise-grade security features!

---

## 📧 Need Help?

If you encounter any issues during setup:

1. **Check the troubleshooting section** above
2. **Review the error messages** carefully
3. **Verify all environment variables** are set correctly
4. **Ensure all prerequisites** are properly installed

**Remember:** This is an enterprise-grade system with advanced security features. Take your time with the setup process and ensure each step is completed correctly.

---

<p align="center">
  🛡️ <strong>Secure IAC Data Management System</strong> 🛡️
</p>

<p align="center">
  <strong>Enterprise Security • GDPR Compliance • Production Ready</strong>
</p>
