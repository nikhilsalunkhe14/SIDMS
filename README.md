# 🛡️ SIDMS — Secure IAC Data Management System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SIDMS** is an enterprise-grade **secure data management system** built with security at its core. It delivers advanced security features including AES-256 encryption, multi-factor authentication (MFA), comprehensive audit logging, secure key management, and full GDPR compliance for managing student academic profiles and administrative data.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Tech Stack](#-tech-stack)
- [Architecture Overview](#-architecture-overview)
- [Security Features](#-security-features)
- [Compliance Features](#-compliance-features)
- [Database Schema](#-database-schema)
- [Setup Instructions](#-setup-instructions)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Security Implementation](#-security-implementation)
- [License](#-license)

---

## 🌐 Project Overview

SIDMS (Secure IAC Data Management System) is a comprehensive, production-ready data management solution designed for organizations requiring enterprise-grade security, compliance, and audit capabilities for managing sensitive academic and administrative data.

### 🎯 Key Highlights

- **🔐 Advanced Authentication** — JWT-based authentication with TOTP multi-factor authentication
- **🛡️ AES-256 Encryption** — Field-level encryption for all sensitive data
- **🔑 Secure Key Management** — Automated key rotation, backup, and versioning
- **📋 GDPR Compliance** — Full compliance framework with data subject rights
- **📊 Comprehensive Audit Trail** — Complete activity logging with IP tracking
- **👥 Role-Based Access Control** — Fine-grained permissions for users and admins
- **🔒 HTTPS Support** — SSL/TLS encryption for data in transit
- **📱 MFA Ready** — TOTP-based 2FA with backup codes

---

## 🧰 Tech Stack

### Backend

| Technology          | Version | Purpose                              |
|---------------------|---------|--------------------------------------|
| Python              | 3.10+   | Core language                        |
| Flask               | 2.3+    | Web framework                       |
| PyJWT              | 2.8+    | JWT authentication                  |
| PyMongo             | 4.5+    | MongoDB driver                      |
| PyOTP               | 2.9+    | TOTP-based MFA                     |
| QRCode              | 8.2+    | QR code generation                  |
| Cryptography        | 41.0+   | AES-256 encryption                 |
| Flask-CORS          | 4.0+    | Cross-origin resource sharing        |
| python-dotenv       | 1.0+    | Environment variable management       |

### Frontend

| Technology          | Version | Purpose                              |
|---------------------|---------|--------------------------------------|
| React               | 18+     | UI framework                         |
| Vite                | 4+      | Build tool & dev server              |
| React Router DOM    | 6+      | Client-side routing                  |
| Axios               | 1.3+    | HTTP client for API calls            |
| CSS3                | —       | Styling with Grid/Flexbox           |

### Database & Infrastructure

| Technology          | Purpose                              |
|---------------------|--------------------------------------|
| MongoDB Atlas       | Cloud database (NoSQL)               |
| JWT                | Stateless authentication tokens        |
| TOTP               | Time-based one-time passwords         |
| AES-256            | Symmetric encryption                 |

---

## 🏛️ Architecture Overview

### Security-First Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Pages → API Client → JWT/MFA → REST Endpoints)          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS (TLS 1.2+)
┌──────────────────────────▼──────────────────────────────────┐
│                   Flask Backend                             │
│  Auth Routes → MFA Routes → Admin Routes → Compliance       │
├─────────────────────────────────────────────────────────────┤
│                   Security Layer                            │
│  JWT Middleware → MFA Service → Encryption Service          │
├─────────────────────────────────────────────────────────────┤
│                   Service Layer                             │
│  Auth Service → Key Manager → Compliance Service           │
├─────────────────────────────────────────────────────────────┤
│                 MongoDB Atlas Database                       │
│  Users → Profiles → Audit Logs → Compliance Data            │
└─────────────────────────────────────────────────────────────┘
```

### Authentication & MFA Flow

```
 ┌──────────┐     ┌─────────────────┐     ┌───────────┐     ┌─────────┐     ┌──────────────────┐
 │ Login    │────▶│ Password Auth  │────▶│ MFA Check │────▶│ TOTP    │────▶│ Access Granted   │
 │ (Creds)  │     │ (JWT Token)    │     │ Required? │     │ Verify  │     │ (Full Token)    │
 └──────────┘     └─────────────────┘     └───────────┘     └─────────┘     └────────┬─────────┘
                                                                                     │
                                                                                 Backup Codes
```

### Encryption & Key Management

```
Plaintext Data ──▶ AES-256 Encrypt ──▶ Base64 ──▶ Stored in MongoDB
                        │
                   Key Manager Service
                  (Rotation + Backup)

Stored Data ──▶ Base64 Decode ──▶ AES-256 Decrypt ──▶ Plaintext Response
                        │
                   Current Key Version
```

---

## 🔒 Security Features

### 🔐 Authentication & Authorization
- **JWT Authentication** — Stateless tokens with role claims
- **TOTP-based MFA** — Time-based one-time passwords (Google Authenticator compatible)
- **Role-Based Access Control** — Admin and user role separation
- **Session Management** — Secure token handling and expiration
- **Backup Codes** — Account recovery with one-time use codes

### 🛡️ Data Protection
- **AES-256 Encryption** — Field-level encryption for sensitive data
- **Secure Key Management** — Key rotation, backup, and versioning
- **TLS/SSL Support** — Encrypted data transmission
- **Environment Variables** — No hardcoded secrets
- **Input Validation** — Comprehensive input sanitization

### 📊 Audit & Monitoring
- **Comprehensive Audit Trail** — All actions logged with user, IP, timestamp
- **Security Headers** — XSS protection, content security policy
- **Access Logging** — Detailed access attempt tracking
- **Error Handling** — Secure error responses without information leakage

---

## 📋 Compliance Features

### 🇪🇺 GDPR Compliance
- **Data Subject Rights** — Access, portability, erasure, correction
- **Consent Management** — Granular consent tracking and withdrawal
- **Data Retention Policies** — Automated cleanup based on configurable policies
- **Data Minimization** — Only collect necessary data
- **Privacy by Design** — Built-in privacy controls

### 📊 Compliance Tools
- **Data Export** — GDPR-compliant data portability
- **Automated Deletion** — Right to be forgotten implementation
- **Consent Tracking** — Complete consent history
- **Compliance Reporting** — Automated compliance status reports
- **Audit Documentation** — Complete compliance audit trail

---

## 🗄️ Database Schema

### MongoDB Collections

```javascript
// Users Collection
{
  _id: ObjectId,
  username: String,
  email: String,
  password: String (BCrypt hashed),
  role: String (ROLE_USER/ROLE_ADMIN),
  created_at: Date,
  updated_at: Date
}

// Member Profiles Collection
{
  _id: ObjectId,
  user_id: String,
  full_name: String (AES-256 encrypted),
  email: String (AES-256 encrypted),
  phone_number: String (AES-256 encrypted),
  address: String (AES-256 encrypted),
  student_id: String (AES-256 encrypted),
  degree: String (AES-256 encrypted),
  resume_url: String (AES-256 encrypted),
  status: String,
  created_at: Date,
  updated_at: Date
}

// Audit Logs Collection
{
  _id: ObjectId,
  user_id: String,
  user_name: String,
  action: String,
  details: Object,
  ip_address: String,
  timestamp: Date
}

// User MFA Collection
{
  _id: ObjectId,
  user_id: String,
  secret: String,
  enabled: Boolean,
  enabled_at: Date,
  backup_codes_generated: Boolean,
  last_backup_generation: Date
}

// Compliance Data Collections
{
  // user_consents, data_subject_requests, 
  // retention_policies, deletion_records
}
```

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.10+** — [Download](https://python.org/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **MongoDB Atlas Account** — [Sign up](https://www.mongodb.com/atlas)
- **Git** — [Download](https://git-scm.com/)

### 1. Clone Repository

```bash
git clone <repository-url>
cd SIDMS
```

### 2. Backend Setup

```bash
# Navigate to backend
cd sidms-python-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install Flask Flask-CORS PyJWT pymongo python-dotenv pyotp qrcode[pil] cryptography bcrypt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd sidms-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Environment Configuration

Create `.env` file in `sidms-python-backend/`:

```bash
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sidms

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRES_IN=3600

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Email (Optional - for OTP/verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Run Applications

**Backend:**
```bash
cd sidms-python-backend
python app.py
```
Backend runs on **http://localhost:5000**

**Frontend:**
```bash
cd sidms-frontend
npm run dev
```
Frontend runs on **http://localhost:5173**

---

## 🔐 Environment Variables

| Variable              | Description                                      | Required | Default                    |
|-----------------------|--------------------------------------------------|----------|----------------------------|
| `MONGODB_URI`        | MongoDB Atlas connection string                     | Yes      | —                          |
| `JWT_SECRET_KEY`      | JWT signing secret key                           | Yes      | —                          |
| `JWT_ACCESS_TOKEN_EXPIRES_IN` | JWT token expiration in seconds          | No       | `3600` (1 hour)           |
| `ENCRYPTION_KEY`     | AES-256 encryption key (32 bytes)               | Yes      | —                          |
| `SMTP_SERVER`        | SMTP server for emails                           | No       | —                          |
| `SMTP_PORT`          | SMTP port                                      | No       | `587`                      |
| `SMTP_USERNAME`      | SMTP username                                   | No       | —                          |
| `SMTP_PASSWORD`      | SMTP password                                   | No       | —                          |

---

## 📡 API Endpoints

### Authentication (`/api/auth`) — Public
| Method | Endpoint               | Description                                        |
|--------|------------------------|----------------------------------------------------|
| POST   | `/api/auth/login`      | User login with password and MFA                     |
| POST   | `/api/auth/complete-mfa-login` | Complete MFA verification                  |

### Member Management (`/api/members`) — Authenticated
| Method | Endpoint              | Description                                        |
|--------|-----------------------|----------------------------------------------------|
| GET    | `/api/my-profile`     | Get user profile                                    |
| POST   | `/api/my-profile`     | Create/update profile                               |
| PUT    | `/api/my-profile`     | Update existing profile                             |

### Admin (`/api/admin`) — Admin Only
| Method | Endpoint                 | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| GET    | `/api/admin/students`     | Get all students                                 |
| GET    | `/api/admin/audit-logs`   | Get audit logs                                   |
| GET    | `/api/admin/key-info`     | Get encryption key information                    |
| POST   | `/api/admin/key-rotate`    | Rotate encryption key                           |
| POST   | `/api/admin/key-backup`    | Backup encryption key                           |

### MFA (`/api/mfa`) — Authenticated
| Method | Endpoint                 | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| POST   | `/api/mfa/setup`          | Setup MFA (QR code generation)                 |
| POST   | `/api/mfa/verify-setup`   | Verify and enable MFA                           |
| POST   | `/api/mfa/verify`         | Verify MFA token during login                    |
| GET    | `/api/mfa/status`         | Get MFA status                                 |

### Compliance (`/api/compliance`) — Authenticated
| Method | Endpoint                      | Description                                          |
|--------|-------------------------------|------------------------------------------------------|
| GET    | `/api/compliance/retention-policies` | Get data retention policies                        |
| POST   | `/api/compliance/consent`             | Record user consent                              |
| GET    | `/api/compliance/consent`             | Get user consents                               |
| POST   | `/api/compliance/data-request`         | Create data subject request                     |
| GET    | `/api/compliance/export-data`          | Export user data (GDPR)                       |
| POST   | `/api/compliance/delete-data`          | Delete user data (right to be forgotten)       |
| GET    | `/api/compliance/report`               | Get compliance report (admin only)             |

---

## 📁 Project Structure

```
SIDMS/
├── sidms-python-backend/                    # Backend Application
│   ├── app.py                             # Main Flask application
│   ├── config/
│   │   └── database.py                    # MongoDB connection
│   ├── models/
│   │   ├── user.py                        # User model
│   │   ├── member_profile.py               # Member profile with encryption
│   │   └── audit_log.py                  # Audit logging
│   ├── routes/
│   │   ├── auth.py                       # Authentication routes
│   │   ├── members.py                    # Member management
│   │   ├── admin.py                      # Admin operations
│   │   ├── mfa.py                        # Multi-factor authentication
│   │   └── compliance.py                 # GDPR compliance
│   ├── services/
│   │   ├── auth_service.py               # Authentication logic
│   │   ├── otp_service.py                # OTP handling
│   │   └── email_service.py              # Email notifications
│   ├── utils/
│   │   ├── encryption.py                 # AES-256 encryption service
│   │   ├── key_manager.py                # Key management system
│   │   ├── mfa_service.py                # MFA service
│   │   ├── compliance_service.py          # GDPR compliance
│   │   └── validators.py                 # Input validation
│   ├── middleware/
│   │   └── auth.py                      # JWT middleware
│   ├── compliance/                        # Compliance directory
│   │   ├── GDPR_COMPLIANCE.md            # Compliance documentation
│   │   ├── user_consents.json             # User consent records
│   │   ├── retention_policies.json        # Data retention policies
│   │   └── data_subject_requests.json     # GDPR requests
│   ├── keys/                             # Key storage directory
│   │   ├── current_key.json               # Current encryption key
│   │   ├── key_history.json              # Key operation history
│   │   └── backup_key_*.json             # Key backups
│   ├── backup_codes/                      # MFA backup codes
│   ├── ssl/                             # SSL certificates
│   ├── requirements.txt                   # Python dependencies
│   └── .env                             # Environment variables
│
├── sidms-frontend/                        # Frontend Application
│   ├── public/
│   │   └── index.html                   # Main HTML file
│   ├── src/
│   │   ├── components/                   # Reusable components
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── Loading.jsx
│   │   ├── pages/                        # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── MemberProfile.jsx
│   │   │   ├── AuditLogs.jsx
│   │   │   └── Compliance.jsx
│   │   ├── utils/                        # Utility functions
│   │   │   └── apiClient.js              # API client configuration
│   │   ├── hooks/                        # Custom React hooks
│   │   ├── styles/                       # CSS files
│   │   │   └── AdminDashboard.css
│   │   ├── App.jsx                       # Main App component
│   │   └── main.jsx                      # Entry point
│   ├── package.json                       # Dependencies
│   └── vite.config.js                    # Vite configuration
│
├── README.md                              # This file
└── LICENSE                               # MIT License
```

---

## 🔐 Security Implementation

### 🔑 Key Management System
- **Automated Key Rotation** — Schedule-based key updates
- **Secure Key Storage** — Encrypted file-based storage
- **Key Versioning** — Track key history and versions
- **Backup & Recovery** — Automated key backup system
- **Audit Trail** — Complete key operation logging

### 🛡️ Encryption Implementation
```python
# AES-256 Encryption Example
from utils.encryption import encryption_service

# Encrypt sensitive data
encrypted_data = encryption_service.encrypt_field("sensitive_info")

# Decrypt sensitive data
decrypted_data = encryption_service.decrypt_field(encrypted_data)
```

### 📱 MFA Implementation
```python
# TOTP Setup
from utils.mfa_service import mfa_service

# Generate secret and QR code
secret = mfa_service.generate_secret()
qr_data = mfa_service.generate_qr_code(email, secret)

# Verify TOTP token
is_valid = mfa_service.verify_token(secret, user_token)
```

### 📋 Compliance Implementation
```python
# GDPR Compliance
from utils.compliance_service import compliance_service

# Record consent
compliance_service.record_consent(user_id, consent_type, True)

# Export user data
user_data = compliance_service.export_user_data(user_id)

# Delete user data (right to be forgotten)
compliance_service.delete_user_data(user_id, "User request")
```

---

## 🎯 Security Best Practices Implemented

### ✅ Authentication Security
- **Strong Password Policies** — Enforced password complexity
- **Multi-Factor Authentication** — TOTP-based 2FA
- **Secure Session Management** — JWT with proper expiration
- **Rate Limiting** — Prevent brute force attacks
- **Account Lockout** — After failed attempts

### ✅ Data Protection
- **Encryption at Rest** — AES-256 for sensitive data
- **Encryption in Transit** — TLS/SSL for all communications
- **Key Management** — Secure key storage and rotation
- **Data Minimization** — Only collect necessary data
- **Secure Backup** — Encrypted backup procedures

### ✅ Compliance & Privacy
- **GDPR Compliant** — Full regulation implementation
- **Consent Management** — Granular consent tracking
- **Data Subject Rights** — Access, portability, deletion
- **Audit Trail** — Complete activity logging
- **Privacy by Design** — Built-in privacy controls

---

## 📄 License

This project is licensed under **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 🏆 Project Achievements

### ✅ Security Features Completed
- [x] **AES-256 Encryption** — Field-level data encryption
- [x] **Multi-Factor Authentication** — TOTP-based 2FA
- [x] **Secure Key Management** — Rotation and backup
- [x] **Comprehensive Audit Trail** — Complete activity logging
- [x] **Role-Based Access Control** — Admin/user separation
- [x] **HTTPS/SSL Support** — Secure data transmission
- [x] **Input Validation** — Comprehensive sanitization
- [x] **Security Headers** — XSS and CSRF protection

### ✅ Compliance Features Completed
- [x] **GDPR Compliance** — Full regulation implementation
- [x] **Data Subject Rights** — Access, portability, erasure
- [x] **Consent Management** — Granular consent tracking
- [x] **Data Retention Policies** — Automated cleanup
- [x] **Compliance Reporting** — Automated status reports
- [x] **Privacy Controls** — Built-in privacy features

---

<p align="center">
  Built with ❤️ using <strong>Python Flask</strong> and <strong>React</strong>
</p>

<p align="center">
  🛡️ <strong>Enterprise-Grade Security & Compliance</strong> 🛡️
</p>
