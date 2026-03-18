from flask import Blueprint, request, jsonify
from models.member_profile import MemberProfile
from models.audit_log import AuditLog
from middleware.auth import token_required
from datetime import datetime
from utils.validators import validate_profile_data
from utils.encryption import encryption_service

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
        print(f"Profile data received: {data}")  # Debug line
        
        # Validate input
        validation_result = validate_profile_data(data)
        print(f"Validation result: {validation_result}")  # Debug line
        
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message']
            }), 400
        
        # Check if profile already exists
        existing_profile = MemberProfile.find_by_user_id(user_id)
        print(f"Existing profile: {existing_profile}")  # Debug line
        
        if existing_profile:
            return jsonify({
                'success': False,
                'message': 'Profile already exists'
            }), 400
        
        # Create profile
        print("Creating new profile...")  # Create new profile
        new_profile = MemberProfile(
            user_id=user_id,
            full_name=data['full_name'],
            email=data['email'],
            phone_number=data['phone_number'],
            residential_address=data['residential_address'],  # NEW
            college_name=data['college_name'],                # NEW
            degree=data.get('degree', ''),  # Handle optional degree field
            resume_url=data.get('resume_url', ''),
            student_id=data.get('student_id', '')
        )
        
        profile_id = new_profile.save()
        
        # Log profile creation with user name
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_name = data.get('full_name', 'Unknown User')
        AuditLog.log_profile_create(user_id, profile_id, client_ip)
        
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile_id': profile_id
        }), 201
        
    except Exception as e:
        print(f"Error in create_my_profile: {e}")  # Debug line
        import traceback
        traceback.print_exc()  # Debug line
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
            # Log profile access with user name
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_name = profile.full_name if profile else user_id
            AuditLog.log_profile_view(user_id, profile.id, client_ip)
            
            # Get raw profile data and decrypt it directly
            from config.database import db
            raw_profile_data = db.member_profiles.find_one({"user_id": user_id})
            
            if raw_profile_data:
                # Decrypt sensitive fields directly
                try:
                    decrypted_data = {
                        "user_id": raw_profile_data.get("user_id"),
                        "full_name": encryption_service.decrypt_field(raw_profile_data.get('full_name', '')),
                        "email": encryption_service.decrypt_field(raw_profile_data.get('email', '')),
                        "phone_number": encryption_service.decrypt_field(raw_profile_data.get('phone_number', '')),
                        "residential_address": encryption_service.decrypt_field(raw_profile_data.get('residential_address', '')),  # NEW
                        "college_name": encryption_service.decrypt_field(raw_profile_data.get('college_name', '')),              # NEW
                        "degree": encryption_service.decrypt_field(raw_profile_data.get('degree', '')),
                        "student_id": encryption_service.decrypt_field(raw_profile_data.get('student_id', '')),
                        "resume_url": encryption_service.decrypt_field(raw_profile_data.get('resume_url', '')),
                        "status": raw_profile_data.get("status", "active"),
                        "created_at": raw_profile_data.get("created_at"),
                        "updated_at": raw_profile_data.get("updated_at")
                    }
                    
                    print(f"DEBUG: Direct decryption successful - Name: {decrypted_data['full_name']}")
                    
                    return jsonify({
                        'success': True,
                        'profile': decrypted_data
                    }), 200
                    
                except Exception as e:
                    print(f"DEBUG: Direct decryption failed: {e}")
                    # Fallback to encrypted data
                    return jsonify({
                        'success': True,
                        'profile': {
                            "full_name": "Decryption Error",
                            "email": "Decryption Error",
                            "phone_number": "Decryption Error",
                            "residential_address": "Decryption Error",
                            "college_name": "Decryption Error",
                            "degree": "Decryption Error",
                            "student_id": "Decryption Error",
                            "resume_url": "Decryption Error",
                            "status": "active"
                        }
                    }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Profile not found'
                }), 404
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
@token_required
def update_my_profile():
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        
        # Validate input data
        from utils.validators import validate_profile_data
        validation_result = validate_profile_data(data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message']
            }), 400
        
        # Check if profile exists
        existing_profile = MemberProfile.find_by_user_id(user_id)
        if not existing_profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found. Please create a profile first.'
            }), 404
        
        print(f"Updating profile for user: {user_id}")  # Debug line
        
        # Update profile fields
        changed_fields = []
        
        # Get current values for comparison (handle encrypted data)
        current_name = existing_profile.full_name or ""
        current_email = existing_profile.email or ""
        current_phone = existing_profile.phone_number or ""
        current_residential_address = existing_profile.residential_address or ""  # NEW
        current_college_name = existing_profile.college_name or ""              # NEW
        current_degree = existing_profile.degree or ""
        current_resume_url = existing_profile.resume_url or ""
        current_student_id = existing_profile.student_id or ""
        
        # Check for changes
        if data.get('full_name') and data.get('full_name') != current_name:
            changed_fields.append('full_name')
        if data.get('email') and data.get('email') != current_email:
            changed_fields.append('email')
        if data.get('phone_number') and data.get('phone_number') != current_phone:
            changed_fields.append('phone_number')
        if data.get('residential_address') and data.get('residential_address') != current_residential_address:  # NEW
            changed_fields.append('residential_address')
        if data.get('college_name') and data.get('college_name') != current_college_name:  # NEW
            changed_fields.append('college_name')
        if data.get('degree') and data.get('degree') != current_degree:
            changed_fields.append('degree')
        if data.get('resume_url') and data.get('resume_url') != current_resume_url:
            changed_fields.append('resume_url')
        if data.get('student_id') and data.get('student_id') != current_student_id:
            changed_fields.append('student_id')
        
        # Create new profile with updated data (this will encrypt the data properly)
        try:
            print(f"DEBUG: Creating updated profile for user: {user_id}")
            updated_profile = MemberProfile(
                user_id=user_id,
                full_name=data.get('full_name', current_name),
                email=data.get('email', current_email),
                phone_number=data.get('phone_number', current_phone),
                residential_address=data.get('residential_address', current_residential_address),
                college_name=data.get('college_name', current_college_name),
                degree=data.get('degree', current_degree),
                resume_url=data.get('resume_url', current_resume_url),
                student_id=data.get('student_id', current_student_id),
                status=existing_profile.status
            )
            print(f"DEBUG: MemberProfile created successfully")
        except Exception as e:
            print(f"DEBUG: Error creating MemberProfile: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Profile creation error: {str(e)}'
            }), 500
        
        # Copy the ID and creation time
        updated_profile.id = existing_profile.id
        updated_profile.created_at = existing_profile.created_at if isinstance(existing_profile.created_at, datetime) else datetime.utcnow()
        updated_profile.updated_at = datetime.utcnow()
        
        # Save updated profile
        try:
            updated_profile.update()
            print(f"DEBUG: Profile update in database successful")
        except Exception as e:
            print(f"DEBUG: Error updating database: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Database update error: {str(e)}'
            }), 500
        
        print(f"Profile updated successfully for user: {user_id}")  # Debug line
        
        # Log detailed profile update with user name
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_name = data.get('full_name', current_name) or user_id
        AuditLog.log_profile_update(user_id, updated_profile.id, changed_fields, client_ip)
        
        # Return decrypted data using the same method as GET route
        from config.database import db
        raw_profile_data = db.member_profiles.find_one({"user_id": user_id})
        
        if raw_profile_data:
            try:
                decrypted_data = {
                    "user_id": raw_profile_data.get("user_id"),
                    "full_name": encryption_service.decrypt_field(raw_profile_data.get('full_name', '')),
                    "email": encryption_service.decrypt_field(raw_profile_data.get('email', '')),
                    "phone_number": encryption_service.decrypt_field(raw_profile_data.get('phone_number', '')),
                    "residential_address": encryption_service.decrypt_field(raw_profile_data.get('residential_address', '')),
                    "college_name": encryption_service.decrypt_field(raw_profile_data.get('college_name', '')),
                    "degree": encryption_service.decrypt_field(raw_profile_data.get('degree', '')),
                    "student_id": encryption_service.decrypt_field(raw_profile_data.get('student_id', '')),
                    "resume_url": encryption_service.decrypt_field(raw_profile_data.get('resume_url', '')),
                    "status": raw_profile_data.get("status", "active"),
                    "created_at": raw_profile_data.get("created_at"),
                    "updated_at": raw_profile_data.get("updated_at")
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': decrypted_data
                }), 200
                
            except Exception as e:
                print(f"DEBUG: Decryption error in update: {e}")
                # Fallback to basic response
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': {
                        "user_id": user_id,
                        "full_name": data.get('full_name', 'Decryption Error'),
                        "email": data.get('email', 'Decryption Error'),
                        "phone_number": data.get('phone_number', 'Decryption Error'),
                        "residential_address": data.get('residential_address', 'Decryption Error'),
                        "college_name": data.get('college_name', 'Decryption Error'),
                        "degree": data.get('degree', 'Decryption Error'),
                        "student_id": data.get('student_id', 'Decryption Error'),
                        "resume_url": data.get('resume_url', 'Decryption Error'),
                        "status": "active"
                    }
                }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
        
    except Exception as e:
        print(f"Error updating profile: {e}")  # Debug line
        import traceback
        traceback.print_exc()  # Debug line
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
