# SIDMS Python Backend

Secure IAC Data Management System - Python Flask Backend with MongoDB Atlas

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Edit `.env` file with your settings:
- MongoDB Atlas connection string
- Gmail credentials
- JWT secret key
- AES encryption key

### 3. Run Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📋 Features

### Authentication
- ✅ User registration with email verification
- ✅ Login with 2-factor authentication (OTP)
- ✅ JWT token-based authentication
- ✅ Role-based access control (RBAC)

### User Management
- ✅ Admin, Manager, Member roles
- ✅ Profile management with encryption
- ✅ Audit logging
- ✅ User enable/disable

### Security
- ✅ AES-256 encryption for sensitive data
- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Input validation and sanitization

## 🛠 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-otp` - OTP verification
- `POST /api/auth/verify-email` - Email verification

### Member Management
- `POST /api/members/me` - Create profile
- `GET /api/members/me` - Get my profile
- `PUT /api/members/me` - Update my profile
- `GET /api/members/{id}` - Get profile (admin/manager)
- `GET /api/members` - Get all profiles (admin/manager)
- `DELETE /api/members/{id}` - Delete profile

### Admin Functions
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/{id}` - Get user details
- `POST /api/admin/users/{id}/assign-role` - Assign role
- `POST /api/admin/users/{id}/enable` - Enable user
- `POST /api/admin/users/{id}/disable` - Disable user
- `GET /api/admin/audit-logs` - Get audit logs

### Utility
- `GET /health` - Health check
- `GET /` - API info
- `GET /api/test-email` - Test email service

## 🔧 Default Credentials

Admin User:
- Username: `admin`
- Password: `Admin@123`
- Role: `ROLE_ADMIN`

## 📊 Database Collections

- `users` - User accounts
- `member_profiles` - Member profiles with encrypted data
- `otps` - One-time passwords
- `audit_logs` - System audit trail

## 🌐 Environment Variables

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES_IN=3600

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AES Encryption
AES_KEY=your-32-byte-encryption-key

# Application
FLASK_ENV=development
FLASK_PORT=5000
```

## 🔒 Security Features

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Encryption**: AES-256 for sensitive data
4. **Validation**: Input validation and sanitization
5. **Audit Trail**: Complete audit logging
6. **Password Security**: bcrypt hashing

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📱 Frontend Integration

The backend provides REST APIs that can be consumed by:
- React Native mobile app
- React web app
- Any HTTP client

## 🐛 Troubleshooting

1. **MongoDB Connection**: Check Atlas IP whitelist
2. **Email Service**: Verify Gmail app password
3. **JWT Token**: Check secret key configuration
4. **Encryption**: Ensure AES key is 32 bytes

## 📞 Support

For issues and questions, check the logs and ensure all environment variables are properly configured.
