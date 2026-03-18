import re
from email_validator import validate_email, EmailNotValidError

def validate_registration_data(data):
    """Validate user registration data"""
    errors = []
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # Username validation
    if not username:
        errors.append('Username is required')
    elif len(username) < 3:
        errors.append('Username must be at least 3 characters long')
    elif len(username) > 50:
        errors.append('Username must be less than 50 characters')
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append('Username can only contain letters, numbers, and underscores')
    
    # Email validation
    if not email:
        errors.append('Email is required')
    else:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(f'Invalid email: {str(e)}')
    
    # Password validation
    if not password:
        errors.append('Password is required')
    elif len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    elif len(password) > 128:
        errors.append('Password must be less than 128 characters')
    elif not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    elif not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    elif not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    if errors:
        return {
            'valid': False,
            'message': '; '.join(errors)
        }
    
    return {
        'valid': True,
        'message': 'Validation successful'
    }

def validate_profile_data(data):
    """Validate member profile data"""
    errors = []
    
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone_number = data.get('phone_number', '').strip()
    residential_address = data.get('residential_address', '').strip()
    college_name = data.get('college_name', '').strip()
    
    # Full name validation
    if not full_name:
        errors.append('Full name is required')
    elif len(full_name) < 2:
        errors.append('Full name must be at least 2 characters long')
    elif len(full_name) > 100:
        errors.append('Full name must be less than 100 characters')
    
    # Email validation
    if not email:
        errors.append('Email is required')
    else:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(f'Invalid email: {str(e)}')
    
    # Phone number validation
    if not phone_number:
        errors.append('Phone number is required')
    elif not re.match(r'^\+?[\d\s\-\(\)]{10,}$', phone_number):
        errors.append('Invalid phone number format')
    
    # Residential address validation
    if not residential_address:
        errors.append('Residential address is required')
    elif len(residential_address) < 10:
        errors.append('Residential address must be at least 10 characters long')
    elif len(residential_address) > 500:
        errors.append('Residential address must be less than 500 characters')
    
    # College name validation
    if not college_name:
        errors.append('College name is required')
    elif len(college_name) < 2:
        errors.append('College name must be at least 2 characters long')
    elif len(college_name) > 100:
        errors.append('College name must be less than 100 characters')
    
    # Student ID validation (optional)
    student_id = data.get('student_id', '').strip()
    if student_id:  # Only validate if provided
        if len(student_id) < 5:
            errors.append('Student ID must be at least 5 characters long')
        elif len(student_id) > 50:
            errors.append('Student ID must be less than 50 characters')
    
    # Resume URL validation (optional) - enhanced for professional use
    resume_url = data.get('resume_url', '').strip()
    # Resume is optional, but if provided, validate it properly
    if resume_url:
        # Accept professional resume platforms
        valid_patterns = [
            r'^https?://docs\.google\.com/',  # Google Docs
            r'^https?://drive\.google\.com/',  # Google Drive
            r'^https?://linkedin\.com/',        # LinkedIn
            r'^https?://.*\.linkedin\.com/',    # LinkedIn variations
            r'^https?://dropbox\.com/',         # Dropbox
            r'^https?://.*\.dropbox\.com/',     # Dropbox variations
            r'^https?://',                      # Any other HTTPS/HTTP URL
        ]
        
        is_valid = any(re.match(pattern, resume_url, re.IGNORECASE) for pattern in valid_patterns)
        
        if not is_valid:
            errors.append('Resume URL must be a valid link (Google Docs, LinkedIn, Drive, Dropbox, or any valid URL)')
    
    if errors:
        return {
            'valid': False,
            'message': '; '.join(errors)
        }
    
    return {
        'valid': True,
        'message': 'Validation successful'
    }

def validate_otp_data(data):
    """Validate OTP verification data"""
    errors = []
    
    username = data.get('username', '').strip()
    otp = data.get('otp', '').strip()
    
    # Username validation
    if not username:
        errors.append('Username is required')
    
    # OTP validation
    if not otp:
        errors.append('OTP is required')
    elif not re.match(r'^\d{6}$', otp):
        errors.append('OTP must be 6 digits')
    
    if errors:
        return {
            'valid': False,
            'message': '; '.join(errors)
        }
    
    return {
        'valid': True,
        'message': 'Validation successful'
    }
