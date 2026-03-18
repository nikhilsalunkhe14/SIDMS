from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header with proper Bearer prefix handling
        auth_header = request.headers.get('Authorization')
        print(f"DEBUG: Auth header received: {auth_header}")
        
        if auth_header:
            try:
                # Handle 'Bearer ' prefix correctly
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    token = auth_header
                print(f"DEBUG: Extracted token: {token[:20]}...")
            except IndexError:
                print("DEBUG: Invalid token format - missing Bearer prefix")
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format - expected Bearer <token>'
                }), 401
        
        if not token:
            print("DEBUG: No token provided")
            return jsonify({
                'success': False,
                'message': 'Token is missing - expected Authorization: Bearer <token>'
            }), 401
        
        # Verify token
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        
        print(f"DEBUG: Decoded payload: {payload}")
        
        if payload is None:
            print("DEBUG: Token verification failed - invalid or expired token")
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        # Set user info on request object (allow any authenticated user)
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        
        print(f"DEBUG: Authentication successful - user_id: {request.user_id}, role: {request.user_role}")
        
        return f(*args, **kwargs)
    
    return decorated_function

def token_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header with proper Bearer prefix handling
        auth_header = request.headers.get('Authorization')
        print(f"DEBUG: Auth header received: {auth_header}")
        
        if auth_header:
            try:
                # Handle 'Bearer ' prefix correctly
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    token = auth_header
                print(f"DEBUG: Extracted token: {token[:20]}...")
            except IndexError:
                print("DEBUG: Invalid token format - missing Bearer prefix")
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format - expected Bearer <token>'
                }), 401
        
        if not token:
            print("DEBUG: No token provided")
            return jsonify({
                'success': False,
                'message': 'Token is missing - expected Authorization: Bearer <token>'
            }), 401
        
        # Verify token
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        
        print(f"DEBUG: Decoded payload: {payload}")
        
        if payload is None:
            print("DEBUG: Token verification failed - invalid or expired token")
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        # Check role and provide descriptive error
        user_role = payload.get('role')
        if user_role != 'ROLE_ADMIN':
            print(f"DEBUG: Access denied - role '{user_role}' is not ROLE_ADMIN")
            return jsonify({
                'success': False,
                'message': f'Access denied - requires ROLE_ADMIN, current role: {user_role}'
            }), 403
        
        # Set user info on request object
        request.user_id = payload.get('user_id')
        request.user_role = user_role
        
        print(f"DEBUG: Authentication successful - user_id: {request.user_id}, role: {request.user_role}")
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(request, 'user_role', None)
            
            if not user_role:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('ROLE_ADMIN')(f)

def manager_required(f):
    return role_required('ROLE_ADMIN', 'ROLE_MANAGER')(f)
