from flask import Flask, jsonify
from flask_cors import CORS
from config.database import db_instance
from routes.auth import auth_bp
from routes.members import members_bp
from routes.admin import admin_bp
from routes.mfa import mfa_bp
from routes.compliance import compliance_bp
from utils.validators import validate_otp_data
import os

# Create Flask app
app = Flask(__name__)

# Configure CORS with explicit headers and credentials
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
     headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Add security headers
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(members_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(mfa_bp)
app.register_blueprint(compliance_bp)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'SIDMS Backend is running'
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'SIDMS Backend API',
        'version': '1.0.0',
        'status': 'running'
    }), 200

# Test email endpoint
@app.route('/api/test-email', methods=['GET'])
def test_email():
    try:
        from services.email_service import EmailService
        email_service = EmailService()
        
        result = email_service.send_email(
            "test@example.com",
            "SIDMS Test Email",
            "This is a test email from SIDMS backend."
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send test email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Method not allowed'
    }), 405

# Initialize database connection
def init_db():
    try:
        if db_instance.connect():
            print("✅ Database connected successfully")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

# Create default admin user
def create_default_admin():
    try:
        from models.user import User
        from services.auth_service import AuthService
        
        # Check if admin already exists
        admin_user = User.find_by_username("admin")
        if admin_user:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        auth_service = AuthService()
        result = auth_service.create_user(
            username="admin",
            email="admin@sidms.com",
            password="Admin@123",
            role="ROLE_ADMIN"
        )
        
        if result['success']:
            # Enable the admin user
            auth_service.enable_user(result['user_id'])
            print("✅ Default admin user created successfully")
            print("   Username: admin")
            print("   Password: Admin@123")
        else:
            print(f"❌ Failed to create admin user: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

# Application factory
def create_app():
    # Initialize database
    if not init_db():
        print("⚠️  Warning: Database connection failed. Some features may not work.")
    
    # Create default admin user
    create_default_admin()
    
    return app

if __name__ == '__main__':
    # Create and configure app
    app = create_app()
    
    # Get port from environment or use default
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print("🌐 Starting SIDMS Backend on HTTP...")
    print("🌍 HTTP URL: http://localhost:5000")
    print("� Development mode - no SSL certificate needed")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
