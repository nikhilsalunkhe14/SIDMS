from flask import Blueprint, request, jsonify
from models.member_profile import MemberProfile
from models.user import User
from models.audit_log import AuditLog
from utils.validators import validate_profile_data
from middleware.auth import token_required

members_bp = Blueprint('members', __name__)

@members_bp.route('/api/members/me', methods=['POST'])
@token_required
def create_my_profile():
    try:
        # Get user from JWT token (middleware will set this)
        user_id = getattr(request, 'user_id', None)
        print(f"Profile creation - user_id from middleware: {user_id}")  # Debug line
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        
        # Validate input
        validation_result = validate_profile_data(data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message']
            }), 400
        
        # Check if profile already exists
        existing_profile = MemberProfile.find_by_user_id(user_id)
        if existing_profile:
            return jsonify({
                'success': False,
                'message': 'Profile already exists'
            }), 400
        
        # Create profile
        profile = MemberProfile(
            user_id=user_id,
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            resume_url=data.get('resume_url'),
            government_id=data.get('government_id')
        )
        
        profile_id = profile.save()
        
        AuditLog.log_action(
            user_id,
            "PROFILE_CREATED",
            f"Profile created for user {user_id}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile_id': profile_id
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@members_bp.route('/api/members/me', methods=['GET'])
@token_required
def get_my_profile():
    try:
        # Get user from JWT token (middleware will set this)
        user_id = getattr(request, 'user_id', None)
        print(f"Profile GET - user_id from middleware: {user_id}")  # Debug line
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Get existing profile
        profile = MemberProfile.find_by_user_id(user_id)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': {
                    'full_name': profile.full_name,
                    'email': profile.email,
                    'phone_number': profile.phone_number,
                    'address': profile.address,
                    'resume_url': profile.resume_url,
                    'government_id': profile.government_id,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat()
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@members_bp.route('/api/members/me', methods=['PUT'])
def update_my_profile():
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        
        # Find existing profile
        profile = MemberProfile.find_by_user_id(user_id)
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        # Update profile
        update_data = {}
        allowed_fields = ['full_name', 'email', 'phone_number', 'address', 'resume_url', 'government_id']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            profile.update(**update_data)
            
            AuditLog.log_action(
                user_id,
                "PROFILE_UPDATED",
                f"Profile updated for user {user_id}"
            )
        
        # Return updated profile
        updated_profile = MemberProfile.find_by_user_id(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': updated_profile.to_response_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@members_bp.route('/api/members/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        profile = MemberProfile.find_by_id(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        # Check permissions: can view own profile or admin/manager
        if profile.user_id != user_id and user_role not in ['ROLE_ADMIN', 'ROLE_MANAGER']:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        return jsonify({
            'success': True,
            'profile': profile.to_response_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@members_bp.route('/api/members', methods=['GET'])
def get_all_profiles():
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Only admin and manager can view all profiles
        if user_role not in ['ROLE_ADMIN', 'ROLE_MANAGER']:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        profiles = MemberProfile.find_all()
        profile_list = [profile.to_response_dict() for profile in profiles]
        
        return jsonify({
            'success': True,
            'profiles': profile_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@members_bp.route('/api/members/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        profile = MemberProfile.find_by_id(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        # Check permissions: can delete own profile or admin
        if profile.user_id != user_id and user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        profile.delete()
        
        AuditLog.log_action(
            user_id,
            "PROFILE_DELETED",
            f"Profile {profile_id} deleted"
        )
        
        return jsonify({
            'success': True,
            'message': 'Profile deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
