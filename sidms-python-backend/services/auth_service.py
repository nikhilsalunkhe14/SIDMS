import jwt
import os
from datetime import datetime, timedelta
from models.user import User
from models.audit_log import AuditLog
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY')
        self.token_expiry = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_IN', 3600))
    
    def generate_token(self, user):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        AuditLog.log_action(
            user.id,
            "TOKEN_GENERATED",
            "JWT token generated for user"
        )
        
        return token
    
    def generate_temp_token(self, user):
        """Generate temporary token for MFA verification (5 minutes expiry)"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'temp': True,
            'exp': datetime.utcnow() + timedelta(minutes=5),
            'iat': datetime.utcnow()
        }
        
        temp_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        AuditLog.log_action(
            user.id,
            "TEMP_TOKEN_GENERATED",
            "Temporary token generated for MFA verification"
        )
        
        return temp_token
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID (handles both admin and regular users)"""
        if user_id == 'admin':
            # Return admin user object
            return type('AdminUser', (), {
                'id': 'admin',
                'username': 'iaccloudadmin',
                'email': 'admin@sidms.com',
                'role': 'ROLE_ADMIN'
            })()
        
        # For regular users, you would typically query the database
        # For now, return None as we don't have user storage in this setup
        return None
    
    def authenticate_user(self, username, password):
        try:
            # Check for hardcoded admin credentials first
            if username == "iaccloudadmin" and password == "iaccloud@567":
                # Create admin user object (not stored in DB)
                admin_user = type('AdminUser', (), {
                    'id': 'admin',
                    'username': 'iaccloudadmin',
                    'email': 'admin@iaccloud.com',
                    'role': 'ROLE_ADMIN',
                    'enabled': True
                })()
                
                AuditLog.log_action(
                    'admin',
                    "ADMIN_LOGIN",
                    "Admin authentication successful"
                )
                
                return admin_user
            
            # Regular user authentication
            user = User.find_by_username(username)
            if not user:
                return None
            
            if not user.check_password(password):
                return None
            
            if not user.enabled:
                return None
            
            AuditLog.log_action(
                user.id,
                "LOGIN_ATTEMPT",
                "User authentication successful"
            )
            
            return user
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def create_user(self, username, email, password, role="ROLE_MEMBER"):
        try:
            # Check if user already exists
            if User.find_by_username(username):
                return {"success": False, "message": "Username already exists"}
            
            if User.find_by_email(email):
                return {"success": False, "message": "Email already exists"}
            
            # Create new user
            user = User(username, email, password, role, enabled=False)
            print(f"Created user object: {user}")  # Debug line
            user_id = user.save()
            print(f"User saved with ID: {user_id}")  # Debug line
            
            AuditLog.log_action(
                user_id,
                "USER_CREATED",
                f"New user created with role: {role}"
            )
            
            return {"success": True, "user_id": user_id, "message": "User created successfully"}
            
        except Exception as e:
            print(f"User creation error: {e}")
            return {"success": False, "message": "Internal server error"}
    
    def enable_user(self, user_id):
        try:
            print(f"Looking for user with ID: {user_id}")  # Debug line
            user = User.find_by_id(user_id)
            print(f"Found user: {user}")  # Debug line
            if user:
                print(f"User enabled status before: {user.enabled}")  # Debug line
                user.enable()
                print(f"User enabled status after: {user.enabled}")  # Debug line
                AuditLog.log_action(
                    user.id,
                    "USER_ENABLED",
                    "User account enabled"
                )
                return True
            return False
        except Exception as e:
            print(f"User enable error: {e}")
            return False
    
    def assign_role(self, user_id, new_role):
        try:
            user = User.find_by_id(user_id)
            if user:
                user.update(role=new_role)
                AuditLog.log_action(
                    user.id,
                    "ROLE_ASSIGNED",
                    f"Role changed to: {new_role}"
                )
                return True
            return False
        except Exception as e:
            print(f"Role assignment error: {e}")
            return False
