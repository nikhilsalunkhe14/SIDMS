# 🔐 Admin Password Change Guide

## 📋 Overview

This guide provides step-by-step instructions for changing the default admin credentials in the SIDMS system. **This is a critical security step that must be completed before deployment.**

---

## ⚠️ Why This is Important

The default admin credentials are:
- **Username:** `iaccloudadmin`
- **Password:** `iaccloud@567`

These are hardcoded in the source code and pose a significant security risk if not changed before deployment.

---

## 🚀 Method 1: Automated Script (Recommended)

### Step 1: Run the Password Change Script

```bash
cd sidms-python-backend
python change_admin_password.py
```

### Step 2: Follow the Prompts

The script will:
1. Show you the current credentials
2. Ask for a new username (optional - can keep current)
3. Ask for a new password (required)
4. Confirm the new password
5. Update the code automatically
6. Create a backup of the original file

### Example Output:
```
🔐 SIDMS Admin Password Change Tool
========================================

Current credentials:
  Username: iaccloudadmin
  Password: iaccloud@567

Enter new credentials:
New username (press Enter to keep 'iaccloudadmin'): myadmin
New password: MySecurePassword123!
Confirm new password: MySecurePassword123!

✅ Admin credentials updated successfully!
   New Username: myadmin
   New Password: MySecurePassword123!

✅ Admin credentials changed successfully!
📝 Please remember to update your SETUP_GUIDE.md with the new credentials
🔄 Restart your backend server for changes to take effect
```

---

## 🔧 Method 2: Manual Change

### Step 1: Open the Authentication Service File

Navigate to: `sidms-python-backend/services/auth_service.py`

### Step 2: Locate the Hardcoded Credentials

Find these lines (around line 82):

```python
# Check for hardcoded admin credentials first
if username == "iaccloudadmin" and password == "iaccloud@567":
```

### Step 3: Update the Username and Password

Replace the hardcoded values with your new credentials:

```python
# Check for hardcoded admin credentials first
if username == "YOUR_NEW_USERNAME" and password == "YOUR_NEW_PASSWORD":
```

### Step 4: Update the Admin User Object

Find this section (around line 84-90):

```python
admin_user = type('AdminUser', (), {
    'id': 'admin',
    'username': 'iaccloudadmin',
    'email': 'admin@iaccloud.com',
    'role': 'ROLE_ADMIN',
    'enabled': True
})()
```

Update the username field:

```python
admin_user = type('AdminUser', (), {
    'id': 'admin',
    'username': 'YOUR_NEW_USERNAME',
    'email': 'admin@iaccloud.com',
    'role': 'ROLE_ADMIN',
    'enabled': True
})()
```

### Step 5: Update the Get User Method (Optional)

Also update the username in the `get_user_by_id` method (around line 70):

```python
'username': 'YOUR_NEW_USERNAME',
```

---

## ✅ Verification Steps

### Step 1: Restart the Backend Server

```bash
cd sidms-python-backend
python app.py
```

### Step 2: Test Login

1. Open your browser to `http://localhost:5173`
2. Try logging in with your **new** admin credentials
3. Ensure you can successfully access the admin dashboard

### Step 3: Test Old Credentials (Should Fail)

Try logging in with the old credentials (`iaccloudadmin` / `iaccloud@567`) to ensure they no longer work.

---

## 🔄 Updating Documentation

After changing the password, update these files:

### SETUP_GUIDE.md
Find the "Default Login Credentials" section and update:

```markdown
### Admin Account
- **Username:** `YOUR_NEW_USERNAME`
- **Password:** `YOUR_NEW_PASSWORD`
```

### README.md
If the README contains default credentials, update them as well.

---

## 🛡️ Security Best Practices

### Password Requirements
- **Minimum length:** 8 characters
- **Recommended:** 12+ characters
- **Include:** Uppercase, lowercase, numbers, and special characters
- **Avoid:** Common words, names, or patterns

### Example Strong Passwords
- `SecureAdmin@2025!`
- `MySidmsPass#123`
- `AdminAccess$Secure2025`

### Additional Security Measures
1. **Enable MFA** for the admin account after login
2. **Change passwords regularly** (every 90 days)
3. **Use a password manager** to store credentials
4. **Never share admin credentials** via email or chat
5. **Log out** when finished using the admin panel

---

## 🔍 Troubleshooting

### ❌ "Script not found" Error
```bash
# Ensure you're in the correct directory
cd "e:\CYBER SECURITY - IP-11069\SIDMS-CODE-IP11069\sidms-python-backend"
python change_admin_password.py
```

### ❌ "Permission denied" Error
```bash
# Run as administrator on Windows
# Or check file permissions
```

### ❌ "Login still works with old password"
- **Check if you restarted the backend server**
- **Verify the changes were saved correctly**
- **Check for syntax errors in the modified file**

### ❌ "New password doesn't work"
- **Double-check for typos in the new password**
- **Ensure no extra spaces were added**
- **Verify the file was saved correctly**

---

## 📝 Quick Reference Commands

### Change Password (Automated)
```bash
cd sidms-python-backend
python change_admin_password.py
```

### Restart Backend
```bash
cd sidms-python-backend
python app.py
```

### Test Connection
```bash
curl http://localhost:5000/health
```

---

## 🚨 Important Reminders

1. **ALWAYS change the default password before deployment**
2. **NEVER commit the actual password to version control**
3. **ALWAYS test the new credentials before going live**
4. **REMEMBER to update documentation**
5. **CONSIDER enabling MFA for additional security**

---

## 📞 Need Help?

If you encounter issues:
1. Check the **troubleshooting section** above
2. Verify the **file permissions** and **syntax**
3. Ensure the **backend server is restarted**
4. Review the **error messages** carefully

---

**Document Version:** 1.0  
**Last Updated:** 2025  
**Project:** SIDMS - Secure IAC Data Management System
