from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.otp_service import OTPService
from services.email_service import EmailService
from utils.validators import validate_registration_data
from models.user import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
otp_service = OTPService()
email_service = EmailService()

@auth_bp.route('/api/auth/complete-mfa-login', methods=['POST'])
def complete_mfa_login():
    """Complete login after MFA verification"""
    try:
        data = request.get_json()
        temp_token = data.get('temp_token')
        mfa_token = data.get('mfa_token')
        
        if not temp_token or not mfa_token:
            return jsonify({
                'success': False,
                'message': 'Temporary token and MFA token are required'
            }), 400
        
        # Verify temporary token
        temp_payload = auth_service.verify_token(temp_token)
        if not temp_payload or not temp_payload.get('temp'):
            return jsonify({
                'success': False,
                'message': 'Invalid or expired temporary token'
            }), 401
        
        user_id = temp_payload.get('user_id')
        
        # Verify MFA token
        from utils.mfa_service import mfa_service
        if not mfa_service.verify_user_mfa(user_id, mfa_token):
            return jsonify({
                'success': False,
                'message': 'Invalid MFA token'
            }), 401
        
        # Get user and generate full token
        user = auth_service.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Generate full token
        full_token = auth_service.generate_token(user)
        
        # Log successful MFA login
        AuditLog.log_action(
            user_id,
            "MFA_LOGIN_SUCCESS",
            {"method": "totp"}
        )
        
        return jsonify({
            'success': True,
            'message': 'MFA login successful',
            'token': full_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    except Exception as e:
        print(f"Error completing MFA login: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = validate_registration_data(data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message']
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Create user
        result = auth_service.create_user(username, email, password)
        
        if result['success']:
            # Send verification email
            verification_link = f"http://localhost:5173/verify?user_id={result['user_id']}"
            email_service.send_verification_email(email, verification_link)
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully. Please check your email for verification.'
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        user = auth_service.authenticate_user(username, password)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Check if admin - handle MFA for admin
        if username == "iaccloudadmin":
            # Check if admin has MFA enabled
            from utils.mfa_service import mfa_service
            mfa_status = mfa_service.get_mfa_status(user.id)
            
            if mfa_status.get('enabled', False):
                # MFA is enabled - require MFA verification
                return jsonify({
                    'success': True,
                    'message': 'Password verified. Please complete MFA verification.',
                    'requires_mfa': True,
                    'user_id': user.id,
                    'temp_token': auth_service.generate_temp_token(user)  # Temporary token for MFA verification
                }), 200
            else:
                # MFA not enabled - generate full token
                token = auth_service.generate_token(user)
                return jsonify({
                    'success': True,
                    'message': 'Admin login successful',
                    'token': token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }
                }), 200
        
        # Generate and send OTP for regular users
        otp_result = otp_service.generate_and_send_otp(username)
        
        if otp_result['success']:
            return jsonify({
                'success': True,
                'message': 'OTP sent to your email',
                'user_id': user.id
            }), 200
        else:
            return jsonify(otp_result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        print(f"OTP verification request data: {data}")  # Debug line
        username = data.get('username')
        otp_code = data.get('otp')
        print(f"Extracted username: {username}, otp: {otp_code}")  # Debug line
        
        if not username or not otp_code:
            return jsonify({
                'success': False,
                'message': 'Username and OTP are required'
            }), 400
        
        # Verify OTP
        otp_result = otp_service.verify_otp(username, otp_code)
        print(f"OTP verification result: {otp_result}")  # Debug line
        
        if otp_result['success']:
            # Get user directly since OTP is valid
            user = User.find_by_username(username)
            print(f"Found user by username: {user}")  # Debug line
            
            if user:
                # Enable user if not already enabled (for users created before ObjectId fix)
                if not user.enabled:
                    print(f"Enabling user {username}")  # Debug line
                    user.enable()
                
                # Generate token
                token = auth_service.generate_token(user)
                print(f"Generated token: {token}")  # Debug line
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'role': user.role,
                    'username': user.username,
                    'user_id': user.id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 400
        
        return jsonify(otp_result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        print(f"Verification request data: {data}")  # Debug line
        user_id = data.get('user_id')
        print(f"Extracted user_id: {user_id}")  # Debug line
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Enable user
        if auth_service.enable_user(user_id):
            # Send welcome email
            user = User.find_by_id(user_id)
            if user:
                email_service.send_welcome_email(user.email, user.username)
            
            return jsonify({
                'success': True,
                'message': 'Email verified successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid user ID'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
