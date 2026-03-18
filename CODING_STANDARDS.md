# SIDMS Coding Standards Document
 
## INDEX
1. PURPOSE 2
2. SCOPE 2
3. FILE STRUCTURE 2
3.1. Standard File Conventions 2
3.2. Markdown Files 2
3.3. Common Conventions 3
4. FORMATTING CONVENTIONS 3
4.1. Indentation 3
4.2. Using Capitalization to Aid Readability 3
4.3. Formatting Single Statements 3
4.4. Formatting Declarations 3
4.5. Formatting Multi-line Statements 3
5. NAMING CONVENTIONS 3
6. SCOPING CONVENTIONS 4
6.1. Lexical/Static Scoping 4
6.2. Dynamic Scoping 4
7. COMPILE ERRORS & WARNINGS 4
8. ENFORCING CODING STANDARD 4
9. APPENDICES 5
9.1. Appendix A – Detailed Description of Components 5
 
---
 
## 1 PURPOSE
 
The Coding Standards are the guidelines for software Developers to create uniform coding habits that eases the reading, checking and maintaining code. The intent of these standards is to define a natural style and consistency, yet leave to the authors, the freedom to practice their craft without unnecessary burden.
 
The coding standards shall enable the following:
- Improve Code Quality: Coding standards ensure that code is written consistently, readably, and maintainable manner. This makes it easier for developers to understand and work with the code, leading to higher-quality software.
- Increase Efficiency: By following coding standards, developers can save time by avoiding common mistakes and implementing proven solutions.
- Facilitate Collaboration: It creates a common language that all developers can understand and allows teams to collaborate, share code, and communicate effectively.
- Ensure Compatibility: It ensures that code is compatible with different platforms, browsers, and OS-device combinations.
- Reduce Maintenance Costs: By following established standards, developers can avoid introducing new bugs and make changes to code more quickly and easily.
 
The coding standards should follow the below best practices:
1. Focus on code readability
2. Enable Commenting
3. Formalising Exception Handling
 
---
 
## 2 SCOPE
 
This document describes general software coding standards for code written for Python 3.10+, React 18+, and associated technologies specific to SIDMS (Secure IAC Data Management System) and shall be implemented while developing the code for the said project.
 
---
 
## 3 FILE STRUCTURE
 
The 'File Structure' allow developers to know where files are, when to use specific code, and locate associated results. Not only do file structures streamline productivity, but they also increase code consistency and shareability.
 
### 3.1 Standard File Conventions
 
**Backend (Python Flask):**
```
sidms-python-backend/
├── app.py                    # Main Flask application entry point
├── config/                   # Configuration modules
├── models/                   # Data models and schemas
├── routes/                   # API route handlers
├── services/                 # Business logic services
├── utils/                    # Utility functions and helpers
├── middleware/               # Custom middleware
├── compliance/               # GDPR compliance data
├── keys/                     # Encryption key storage
├── backup_codes/             # MFA backup codes
├── ssl/                      # SSL certificates
└── requirements.txt          # Python dependencies
```
 
**Frontend (React):**
```
sidms-frontend/
├── public/                   # Static assets
├── src/
│   ├── components/           # Reusable UI components
│   ├── pages/               # Page-level components
│   ├── utils/               # Utility functions
│   ├── hooks/               # Custom React hooks
│   ├── styles/              # CSS files
│   ├── App.jsx              # Main application component
│   └── main.jsx             # Application entry point
├── package.json             # Node.js dependencies
└── vite.config.js           # Build configuration
```
 
### 3.2 Markdown Files
 
All markdown files must follow these conventions:
- Use kebab-case for filenames (e.g., `setup-guide.md`)
- Include proper headers with level indicators (# ## ###)
- Use fenced code blocks with language identifiers
- Maintain consistent formatting and spacing
 
### 3.3 Common Conventions
 
- Use relative imports for internal modules
- Environment variables stored in `.env` files
- Configuration separated from application logic
- Security-sensitive data never hardcoded
- All sensitive data must be encrypted at rest
 
---
 
## 4 FORMATTING CONVENTIONS
 
These conventions are all about the positions of line breaks, how many characters should go on a line, and everything in between.
 
### 4.1 Indentation
 
**Python:**
- Use 4 spaces for indentation (never tabs)
- Maximum line length: 88 characters (Black formatter standard)
- Use blank lines to separate logical sections
 
**JavaScript/JSX:**
- Use 2 spaces for indentation
- Maximum line length: 100 characters
- Use semicolons at end of statements
 
### 4.2 Using Capitalization to Aid Readability
 
**Python:**
- snake_case for variables and functions: `user_data`, `encrypt_field()`
- PascalCase for classes: `EncryptionService`, `UserModel`
- UPPER_CASE for constants: `ENCRYPTION_KEY`, `JWT_SECRET`
 
**JavaScript/JSX:**
- camelCase for variables and functions: `userData`, `handleSubmit()`
- PascalCase for components: `UserProfile`, `LoginForm`
- UPPER_CASE for constants: `API_BASE_URL`, `MAX_FILE_SIZE`
 
### 4.3 Formatting Single Statements
 
- One statement per line
- Logical operators surrounded by spaces: `if x > 0 and y < 10:`
- Function calls with space after comma: `func(arg1, arg2, arg3)`
 
### 4.4 Formatting Declarations
 
**Python:**
```python
# Variable declarations
user_id = "12345"
encryption_key = os.getenv('ENCRYPTION_KEY')
 
# Function declarations
def encrypt_sensitive_data(data: str) -> str:
    pass
 
# Class declarations
class EncryptionService:
    def __init__(self):
        pass
```
 
**JavaScript:**
```javascript
// Variable declarations
const userId = "12345";
const encryptionKey = process.env.ENCRYPTION_KEY;
 
// Function declarations
function encryptSensitiveData(data) {
  return data;
}
 
// Arrow functions
const encryptData = (data) => {
  return data;
};
```
 
### 4.5 Formatting Multi-line Statements
 
**Python:**
```python
# Function calls with multiple arguments
result = some_function(
    arg1,
    arg2,
    arg3,
    kwarg1=value1,
    kwarg2=value2
)
 
# Long conditionals
if (condition1 and condition2 and 
    condition3 and condition4):
    pass
```
 
**JavaScript:**
```javascript
// Function calls with multiple arguments
const result = someFunction(
  arg1,
  arg2,
  arg3,
  {
    key1: value1,
    key2: value2
  }
);
 
// Long conditionals
if (condition1 && condition2 && 
    condition3 && condition4) {
  // code
}
```
 
---
 
## 5 NAMING CONVENTIONS
 
Naming conventions make programs more understandable by making them easier to read. They can also give information about the function of the identifier.
 
### Backend (Python)
 
| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_data`, `encrypted_value` |
| Functions | snake_case | `encrypt_field()`, `validate_user()` |
| Classes | PascalCase | `EncryptionService`, `UserModel` |
| Constants | UPPER_CASE | `ENCRYPTION_KEY`, `MAX_RETRY_ATTEMPTS` |
| Private members | underscore_prefix | `_internal_method`, `_private_var` |
| Modules | snake_case | `encryption_service.py`, `user_routes.py` |
 
### Frontend (JavaScript/JSX)
 
| Type | Convention | Example |
|------|------------|---------|
| Variables | camelCase | `userData`, `encryptedValue` |
| Functions | camelCase | `encryptField()`, `validateUser()` |
| Components | PascalCase | `UserProfile`, `LoginForm` |
| Constants | UPPER_CASE | `API_BASE_URL`, `MAX_FILE_SIZE` |
| Private members | underscore_prefix | `_internalMethod`, `_privateVar` |
| Files | kebab-case | `user-profile.jsx`, `api-client.js` |
 
### Database Collections
 
| Collection | Naming | Example |
|------------|--------|---------|
| Users | snake_case | `users`, `user_mfa` |
| Logs | snake_case | `audit_logs`, `access_logs` |
| Profiles | snake_case | `member_profiles` |
| Compliance | snake_case | `user_consents`, `data_requests` |
 
---
 
## 6 SCOPING CONVENTIONS
 
Scoping is generally divided into two types:
 
### 6.1 Lexical/Static Scoping
 
A variable in this scope always refers to its top-level environment. This characteristic of the program text has nothing to do with the call stack at runtime. Static scoping makes it considerably easier to write modular code because a programmer can find out the scope by looking at the code.
 
**Python Example:**
```python
def outer_function():
    outer_var = "I am in outer scope"
 
    def inner_function():
        inner_var = "I am in inner scope"
        print(outer_var)  # Can access outer scope
        print(inner_var)  # Can access inner scope
 
    inner_function()
```
 
### 6.2 Dynamic Scoping
 
With dynamic scope, a global identifier directs to the identifier associated with the most current environment and is unusual in modern languages.
 
**Note:** Dynamic scoping is NOT used in this project. All scoping follows lexical/static conventions.
 
---
 
## 7 COMPILE ERRORS & WARNINGS
 
### 7.1 Errors
 
Errors report problems that make it impossible to compile your program.
 
**Syntax Errors:**
- Misspelled statements, functions, or variables
- Missing brackets, quotes, or colons
- Incorrect indentation in Python
- Invalid JSX syntax in React
 
**Logic Errors:**
- Incorrect use of logical operators
- Infinite loops
- Incorrect variable usage
- Wrong algorithm implementation
 
**Runtime Errors:**
- Null pointer exceptions
- Type errors
- Network connection failures
- Database connection errors
 
**Error Handling Requirements:**
- All database operations must have try-catch blocks
- API endpoints must handle exceptions gracefully
- User input must be validated before processing
- Error messages must not expose sensitive information
 
### 7.2 Warnings
 
Warnings report other unusual conditions in your code that may indicate danger points where you should check to make sure that your program really does what you intend.
 
**Common Warnings to Address:**
- Unused variables and imports
- Deprecated function usage
- Potential security vulnerabilities
- Performance issues
- Missing type hints in Python
 
---
 
## 8 ENFORCING CODING STANDARD
 
### Development Tools
 
**Backend (Python):**
```bash
# Code formatting
pip install black isort flake8
 
# Type checking
pip install mypy
 
# Security scanning
pip install bandit
 
# Run tools
black ./
isort ./
flake8 ./
mypy ./
bandit -r ./
```
 
**Frontend (JavaScript):**
```bash
# Code formatting
npm install --save-dev prettier eslint
 
# Run tools
npx prettier --write ./
npx eslint ./
```
 
### Pre-commit Hooks
 
Configuration for `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```
 
### Code Review Checklist
 
- [ ] Code follows naming conventions
- [ ] Functions are properly documented
- [ ] Error handling is implemented
- [ ] Security best practices are followed
- [ ] No hardcoded secrets
- [ ] Proper input validation
- [ ] Tests are written for critical functions
- [ ] Code is formatted according to standards
 
---
 
## 9 APPENDICES
 
### 9.1 Appendix A – Detailed Description of Components
 
#### Backend Components
 
| Component | Purpose | Key Files |
|-----------|---------|-----------|
| Authentication | JWT-based auth with MFA | `routes/auth.py`, `services/auth_service.py` |
| Encryption | AES-256 field encryption | `utils/encryption.py`, `utils/key_manager.py` |
| Database | MongoDB Atlas integration | `config/database.py`, `models/` |
| Compliance | GDPR compliance features | `routes/compliance.py`, `utils/compliance_service.py` |
| Audit Logging | Security event tracking | `models/audit_log.py` |
 
#### Frontend Components
 
| Component | Purpose | Key Files |
|-----------|---------|-----------|
| Authentication | Login/logout/MFA UI | `pages/Login.jsx`, `pages/OtpVerification.jsx` |
| Dashboard | Main user interface | `pages/Dashboard.jsx`, `pages/AdminDashboard.jsx` |
| Profile Management | User profile CRUD | `pages/ProfileForm.jsx` |
| API Client | Backend communication | `utils/apiClient.js` |
 
#### Security Requirements
 
- All sensitive data must be encrypted using AES-256
- JWT tokens must have expiration and refresh mechanisms
- MFA must be implemented for admin accounts
- All API endpoints must have proper authentication
- Input validation must be implemented for all user inputs
- Audit logs must be maintained for all sensitive operations
 
#### Performance Guidelines
 
- Database queries should use proper indexing
- API responses should be paginated for large datasets
- Frontend should implement lazy loading for heavy components
- Caching should be implemented for frequently accessed data
- Image and file uploads should have size limits
 
---
 
**Document Version:** 1.0  
**Last Updated:** 2025  
**Project:** SIDMS - Secure IAC Data Management System  
**Technologies:** Python 3.10+, Flask 2.3+, React 18+, MongoDB Atlas
 