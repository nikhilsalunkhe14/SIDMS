from flask import Blueprint, request, jsonify
from datetime import datetime
from models.user import User
from models.member_profile import MemberProfile
from models.audit_log import AuditLog
from services.auth_service import AuthService
from bson import ObjectId
from config.database import db
from middleware.auth import token_required_admin
from utils.encryption import encryption_service

admin_bp = Blueprint('admin', __name__)
auth_service = AuthService()

@admin_bp.route('/api/admin/users', methods=['GET'])
@token_required_admin
def get_all_users():
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can view all users
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get all users (excluding passwords)
        users = []
        for user_data in User.find_all():
            user_dict = {
                'id': user_data.id,
                'username': user_data.username,
                'email': user_data.email,
                'role': user_data.role,
                'enabled': user_data.enabled,
                'mfa_enabled': user_data.mfa_enabled,
                'created_at': user_data.created_at.isoformat() if user_data.created_at else None
            }
            users.append(user_dict)
        
        return jsonify({
            'success': True,
            'users': users
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        current_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not current_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can view user details
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'enabled': user.enabled,
            'mfa_enabled': user.mfa_enabled,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'user': user_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/users/<user_id>/assign-role', methods=['POST'])
def assign_role(user_id):
    try:
        current_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not current_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can assign roles
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({
                'success': False,
                'message': 'Role is required'
            }), 400
        
        valid_roles = ['ROLE_ADMIN', 'ROLE_MANAGER', 'ROLE_MEMBER']
        if new_role not in valid_roles:
            return jsonify({
                'success': False,
                'message': 'Invalid role'
            }), 400
        
        # Assign role
        if auth_service.assign_role(user_id, new_role):
            AuditLog.log_action(
                current_user_id,
                "ROLE_ASSIGNED_BY_ADMIN",
                f"Role {new_role} assigned to user {user_id}"
            )
            
            return jsonify({
                'success': True,
                'message': 'Role assigned successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to assign role'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/users/<user_id>/enable', methods=['POST'])
def enable_user(user_id):
    try:
        current_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not current_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can enable users
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Enable user
        if auth_service.enable_user(user_id):
            AuditLog.log_action(
                current_user_id,
                "USER_ENABLED_BY_ADMIN",
                f"User {user_id} enabled"
            )
            
            return jsonify({
                'success': True,
                'message': 'User enabled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to enable user'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/users/<user_id>/disable', methods=['POST'])
def disable_user(user_id):
    try:
        current_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not current_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can disable users
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Prevent admin from disabling themselves
        if user_id == current_user_id:
            return jsonify({
                'success': False,
                'message': 'Cannot disable your own account'
            }), 400
        
        user.disable()
        
        AuditLog.log_action(
            current_user_id,
            "USER_DISABLED_BY_ADMIN",
            f"User {user_id} disabled"
        )
        
        return jsonify({
            'success': True,
            'message': 'User disabled successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# Student-specific routes for admin
@admin_bp.route('/api/admin/students', methods=['GET'])
@token_required_admin
def get_all_students():
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can view all students
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get all member profiles (only active ones)
        profiles = []
        profile_data = db.member_profiles.find({"status": {"$ne": "archived"}})
        
        for profile in profile_data:
            # Get user information
            user = User.find_by_id(profile.get('user_id'))
            if user:
                # Decrypt sensitive fields
                try:
                    decrypted_full_name = encryption_service.decrypt_field(profile.get('full_name', ''))
                    decrypted_email = encryption_service.decrypt_field(profile.get('email', ''))
                    decrypted_phone = encryption_service.decrypt_field(profile.get('phone_number', ''))
                    decrypted_address = encryption_service.decrypt_field(profile.get('address', ''))
                    decrypted_degree = encryption_service.decrypt_field(profile.get('degree', ''))
                    decrypted_student_id = encryption_service.decrypt_field(profile.get('student_id', ''))
                    decrypted_resume_url = encryption_service.decrypt_field(profile.get('resume_url', ''))
                except Exception as e:
                    print(f"Error decrypting profile data: {e}")
                    # Fallback to raw data if decryption fails
                    decrypted_full_name = profile.get('full_name', 'Decryption Error')
                    decrypted_email = profile.get('email', 'Decryption Error')
                    decrypted_phone = profile.get('phone_number', 'Decryption Error')
                    decrypted_address = profile.get('address', 'Decryption Error')
                    decrypted_degree = profile.get('degree', 'Decryption Error')
                    decrypted_student_id = profile.get('student_id', 'Decryption Error')
                    decrypted_resume_url = profile.get('resume_url', 'Decryption Error')
                
                student_info = {
                    'id': str(profile.get('_id')),
                    'user_id': profile.get('user_id'),
                    'full_name': decrypted_full_name,
                    'email': decrypted_email,
                    'phone_number': decrypted_phone,
                    'address': decrypted_address,
                    'degree': decrypted_degree,
                    'student_id': decrypted_student_id,
                    'resume_url': decrypted_resume_url,
                    'created_at': profile.get('created_at'),
                    'updated_at': profile.get('updated_at')
                }
                profiles.append(student_info)
        
        return jsonify({
            'success': True,
            'students': profiles
        }), 200
        
    except Exception as e:
        print(f"Error fetching students: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/student/<student_id>', methods=['GET'])
@token_required_admin
def get_student_detail(student_id):
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can view student details
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get specific member profile
        profile_data = db.member_profiles.find_one({'_id': ObjectId(student_id)})
        
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404
        
        # Log admin access to student profile with names
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        admin_name = "Admin"  # We could get admin name from users table if needed
        student_name = profile_data.get('full_name', 'Unknown Student')
        AuditLog.log_admin_action(user_id, "VIEWED_STUDENT_PROFILE", profile_data.get('user_id'), {
            "profile_id": student_id,
            "student_name": student_name,
            "admin_name": admin_name
        }, client_ip)
        
        # Get user information
        user = User.find_by_id(profile_data.get('user_id'))
        
        # Decrypt sensitive fields
        try:
            decrypted_full_name = encryption_service.decrypt_field(profile_data.get('full_name', ''))
            decrypted_email = encryption_service.decrypt_field(profile_data.get('email', ''))
            decrypted_phone = encryption_service.decrypt_field(profile_data.get('phone_number', ''))
            decrypted_address = encryption_service.decrypt_field(profile_data.get('address', ''))
            decrypted_degree = encryption_service.decrypt_field(profile_data.get('degree', ''))
            decrypted_student_id = encryption_service.decrypt_field(profile_data.get('student_id', ''))
            decrypted_resume_url = encryption_service.decrypt_field(profile_data.get('resume_url', ''))
        except Exception as e:
            print(f"Error decrypting student detail: {e}")
            # Fallback to raw data if decryption fails
            decrypted_full_name = profile_data.get('full_name', 'Decryption Error')
            decrypted_email = profile_data.get('email', 'Decryption Error')
            decrypted_phone = profile_data.get('phone_number', 'Decryption Error')
            decrypted_address = profile_data.get('address', 'Decryption Error')
            decrypted_degree = profile_data.get('degree', 'Decryption Error')
            decrypted_student_id = profile_data.get('student_id', 'Decryption Error')
            decrypted_resume_url = profile_data.get('resume_url', 'Decryption Error')
        
        # Get user information for security details
        user_info = {}
        user_data = db.users.find_one({"_id": ObjectId(profile_data.get('user_id'))})
        if user_data:
            user_info = {
                'username': user_data.get('username'),
                'role': user_data.get('role'),
                'enabled': user_data.get('enabled'),
                'mfa_enabled': user_data.get('mfa_enabled', False),
                'user_created_at': user_data.get('created_at'),
                'user_updated_at': user_data.get('updated_at')
            }
        
        student_info = {
            'id': str(profile_data.get('_id')),
            'user_id': profile_data.get('user_id'),
            'full_name': decrypted_full_name,
            'email': decrypted_email,
            'phone_number': decrypted_phone,
            'address': decrypted_address,
            'degree': decrypted_degree,
            'student_id': decrypted_student_id,
            'resume_url': decrypted_resume_url,
            'status': profile_data.get('status', 'active'),
            'created_at': profile_data.get('created_at'),
            'updated_at': profile_data.get('updated_at'),
            'user_info': user_info  # Added user security information
        }
        
        return jsonify({
            'success': True,
            'student': student_info
        }), 200
        
    except Exception as e:
        print(f"Error fetching student detail: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/student/<student_id>/audit-logs', methods=['GET'])
@token_required_admin
def get_student_audit_logs(student_id):
    """Get audit logs for a specific student"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get audit logs for this student
        logs = []
        audit_data = db.audit_logs.find({"user_id": student_id}).sort("timestamp", -1).limit(50)
        
        for log in audit_data:
            log_dict = {
                'id': str(log.get('_id')),
                'user_id': log.get('user_id'),
                'user_name': log.get('user_name'),
                'action': log.get('action'),
                'details': log.get('details'),
                'ip_address': log.get('ip_address'),
                'timestamp': log.get('timestamp')
            }
            logs.append(log_dict)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total': len(logs)
        }), 200
        
    except Exception as e:
        print(f"Error fetching student audit logs: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/student/<student_id>/export', methods=['GET'])
@token_required_admin
def export_student_data(student_id):
    """Export student data in PDF format for GDPR compliance"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get student profile data
        profile_data = db.member_profiles.find_one({"user_id": student_id})
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'Student profile not found'
            }), 404
        
        # Get user data
        user_data = db.users.find_one({"_id": ObjectId(student_id)})
        
        # Get audit logs
        audit_logs = list(db.audit_logs.find({"user_id": student_id}).sort("timestamp", -1))
        
        # Decrypt sensitive data for export
        try:
            decrypted_full_name = encryption_service.decrypt_field(profile_data.get('full_name', ''))
            decrypted_email = encryption_service.decrypt_field(profile_data.get('email', ''))
            decrypted_phone = encryption_service.decrypt_field(profile_data.get('phone_number', ''))
            decrypted_address = encryption_service.decrypt_field(profile_data.get('address', ''))
            decrypted_degree = encryption_service.decrypt_field(profile_data.get('degree', ''))
            decrypted_student_id = encryption_service.decrypt_field(profile_data.get('student_id', ''))
            decrypted_resume_url = encryption_service.decrypt_field(profile_data.get('resume_url', ''))
        except Exception as e:
            print(f"Error decrypting data for export: {e}")
            return jsonify({
                'success': False,
                'message': 'Failed to decrypt data for export'
            }), 500
        
        # Create export data structure
        export_data = {
            'export_metadata': {
                'export_date': datetime.utcnow().isoformat(),
                'exported_by': user_id,
                'purpose': 'GDPR Data Portability Request',
                'format': 'PDF Document'
            },
            'user_account': {
                'username': user_data.get('username') if user_data else None,
                'email': decrypted_email,
                'role': user_data.get('role') if user_data else None,
                'enabled': user_data.get('enabled') if user_data else None,
                'mfa_enabled': user_data.get('mfa_enabled') if user_data else None,
                'account_created': user_data.get('created_at') if user_data else None,
                'account_updated': user_data.get('updated_at') if user_data else None
            },
            'profile_information': {
                'full_name': decrypted_full_name,
                'phone_number': decrypted_phone,
                'address': decrypted_address,
                'degree': decrypted_degree,
                'student_id': decrypted_student_id,
                'resume_url': decrypted_resume_url,
                'profile_status': profile_data.get('status', 'active'),
                'profile_created': profile_data.get('created_at'),
                'profile_updated': profile_data.get('updated_at')
            },
            'audit_trail': []
        }
        
        # Add audit logs to export
        for log in audit_logs:
            export_data['audit_trail'].append({
                'timestamp': log.get('timestamp'),
                'action': log.get('action'),
                'details': log.get('details'),
                'ip_address': log.get('ip_address')
            })
        
        # Generate PDF
        try:
            print(f"DEBUG: Attempting to import PDF service...")
            from services.pdf_export_service import pdf_export_service
            print(f"DEBUG: PDF service imported successfully")
            
            print(f"DEBUG: Creating PDF with export_data...")
            pdf_data = pdf_export_service.create_student_data_pdf(export_data)
            print(f"DEBUG: PDF generated successfully, size: {len(pdf_data)} bytes")
            
            # Create response with PDF
            from flask import Response
            response = Response(
                pdf_data,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=student_data_export_{decrypted_full_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                }
            )
            
            print(f"DEBUG: Flask response created successfully")
            return response
            
        except Exception as e:
            print(f"DEBUG: Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Failed to generate PDF export: {str(e)}'
            }), 500
        
    except Exception as e:
        print(f"Error exporting student data: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/students/<student_id>/archive', methods=['POST'])
@token_required_admin
def archive_student_profile(student_id):
    """Archive (soft delete) a student profile"""
    try:
        # Get admin user_id from token
        admin_user_id = getattr(request, 'user_id', None)
        if not admin_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Find and update the student profile directly
        result = db.member_profiles.update_one(
            {"user_id": student_id},
            {"$set": {"status": "archived", "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Student profile not found'
            }), 404
        
        # Log the action
        AuditLog.log_action(
            admin_user_id,
            "STUDENT_ARCHIVED",
            f"Admin archived student profile: {student_id}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Student profile archived successfully'
        }), 200
        
    except Exception as e:
        print(f"Error archiving student profile: {e}")  # Debug line
        import traceback
        traceback.print_exc()  # Debug line
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/students/<student_id>/restore', methods=['POST'])
@token_required_admin
def restore_student_profile(student_id):
    """Restore a student profile from archived state"""
    try:
        # Get admin user_id from token
        admin_user_id = getattr(request, 'user_id', None)
        if not admin_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Find and update the student profile directly
        result = db.member_profiles.update_one(
            {"user_id": student_id},
            {"$set": {"status": "active", "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Student profile not found'
            }), 404
        
        # Log the action
        AuditLog.log_action(
            admin_user_id,
            "STUDENT_RESTORED",
            f"Admin restored student profile: {student_id}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Student profile restored successfully'
        }), 200
        
    except Exception as e:
        print(f"Error restoring student profile: {e}")  # Debug line
        import traceback
        traceback.print_exc()  # Debug line
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/students/archived', methods=['GET'])
@token_required_admin
def get_archived_students():
    """Get all archived student profiles"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin can view archived students
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get all archived member profiles
        profiles = []
        profile_data = db.member_profiles.find({"status": "archived"})
        
        for profile in profile_data:
            # Get user information
            user = User.find_by_id(profile.get('user_id'))
            if user:
                student_info = {
                    'id': str(profile.get('_id')),
                    'user_id': profile.get('user_id'),
                    'full_name': profile.get('full_name'),
                    'email': profile.get('email'),
                    'phone': profile.get('phone_number'),
                    'college': profile.get('address'),
                    'degree': profile.get('degree'),
                    'student_id': profile.get('student_id'),
                    'resume_url': profile.get('resume_url'),
                    'status': profile.get('status'),
                    'created_at': profile.get('created_at'),
                    'updated_at': profile.get('updated_at'),
                    'username': user.username
                }
                profiles.append(student_info)
        
        return jsonify({
            'success': True,
            'students': profiles
        }), 200
        
    except Exception as e:
        print(f"Error fetching archived students: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/test-auth', methods=['GET'])
def test_auth():
    """Test route to check authentication"""
    return jsonify({
        'success': True,
        'message': 'Authentication test successful',
        'headers': dict(request.headers)
    }), 200

@admin_bp.route('/api/admin/key-info', methods=['GET'])
@token_required_admin
def get_key_info():
    """Get current encryption key information"""
    try:
        admin_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not admin_user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        from utils.encryption import encryption_service
        
        key_info = encryption_service.get_key_info()
        
        return jsonify({
            'success': True,
            'key_info': key_info,
            'message': 'Key information retrieved successfully'
        }), 200
    
    except Exception as e:
        print(f"Error retrieving key info: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/key-rotate', methods=['POST'])
@token_required_admin
def rotate_key():
    """Rotate encryption key"""
    try:
        admin_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not admin_user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        from utils.key_manager import key_manager
        from utils.encryption import encryption_service
        
        # Rotate the key
        rotation_result = key_manager.rotate_key()
        
        # Refresh encryption service with new key
        encryption_service.refresh_key()
        
        # Log the key rotation
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_admin_action(
            admin_user_id, 
            "KEY_ROTATION", 
            None, 
            {
                "old_version": rotation_result["old_version"],
                "new_version": rotation_result["new_version"],
                "admin_name": "Admin"
            }, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'Key rotated successfully',
            'rotation_result': {
                'old_version': rotation_result["old_version"],
                'new_version': rotation_result["new_version"]
            }
        }), 200
    
    except Exception as e:
        print(f"Error rotating key: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/key-backup', methods=['POST'])
@token_required_admin
def backup_key():
    """Backup encryption key"""
    try:
        admin_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not admin_user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        from utils.key_manager import key_manager
        
        # Create backup
        backup_path = key_manager.backup_key()
        
        # Log the backup
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_admin_action(
            admin_user_id, 
            "KEY_BACKUP", 
            None, 
            {
                "backup_path": backup_path,
                "admin_name": "Admin"
            }, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'Key backed up successfully',
            'backup_path': backup_path
        }), 200
    
    except Exception as e:
        print(f"Error backing up key: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/key-history', methods=['GET'])
@token_required_admin
def get_key_history():
    """Get key operation history"""
    try:
        admin_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not admin_user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        from utils.key_manager import key_manager
        
        history = key_manager.list_history()
        
        return jsonify({
            'success': True,
            'history': history,
            'message': 'Key history retrieved successfully'
        }), 200
    
    except Exception as e:
        print(f"Error retrieving key history: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@admin_bp.route('/api/admin/audit-logs', methods=['GET'])
@token_required_admin
def get_admin_audit_logs():
    """Get all audit logs for admin review"""
    try:
        admin_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not admin_user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        if user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        print("DEBUG: Authentication successful, fetching audit logs")
        
        limit = int(request.args.get('limit', 100))
        action_filter = request.args.get('action', '')
        user_filter = request.args.get('user_id', '')
        
        query = {}
        if action_filter:
            query['action'] = {'$regex': action_filter, '$options': 'i'}
        if user_filter:
            query['user_id'] = user_filter
        
        logs = []
        try:
            log_data = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
            
            for log in log_data:
                log_entry = {
                    'id': str(log.get('_id')),
                    'user_id': log.get('user_id'),
                    'user_name': log.get('user_name'),
                    'action': log.get('action'),
                    'details': log.get('details'),
                    'ip_address': log.get('ip_address'),
                    'timestamp': log.get('timestamp'),
                    'formatted_time': log.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if log.get('timestamp') else 'N/A'
                }
                logs.append(log_entry)
        except Exception as e:
            print(f"DEBUG: Error fetching audit logs: {e}")
            # Return empty logs if collection doesn't exist yet
            logs = []
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total': len(logs),
            'message': f'Found {len(logs)} audit logs'
        }), 200
        
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
