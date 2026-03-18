#!/usr/bin/env python3
"""
MFA (Multi-Factor Authentication) routes for SIDMS
"""

from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.mfa_service import mfa_service
from models.audit_log import AuditLog
from datetime import datetime

mfa_bp = Blueprint('mfa', __name__)

@mfa_bp.route('/api/mfa/setup', methods=['POST'])
@token_required
def setup_mfa():
    """Setup MFA for a user - generate secret and QR code"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Generate new secret
        secret = mfa_service.generate_secret()
        
        # Get user email for QR code
        from config.database import db
        user = db.users.find_one({'_id': user_id})
        user_email = user.get('email', 'user@example.com') if user else 'user@example.com'
        
        # Generate QR code
        qr_data = mfa_service.generate_qr_code(user_email, secret)
        
        # Log MFA setup initiation
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_SETUP_INITIATED", 
            {"user_email": user_email}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'qr_code': qr_data['qr_code'],
            'secret': qr_data['secret'],
            'manual_entry_key': qr_data['manual_entry_key'],
            'message': 'MFA setup initiated. Please verify with your authenticator app.'
        }), 200
    
    except Exception as e:
        print(f"Error setting up MFA: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/verify-setup', methods=['POST'])
@token_required
def verify_mfa_setup():
    """Verify MFA setup and enable it for user"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        secret = data.get('secret')
        token = data.get('token')
        
        if not secret or not token:
            return jsonify({
                'success': False,
                'message': 'Secret and token are required'
            }), 400
        
        # Verify the token
        if not mfa_service.verify_token(secret, token):
            return jsonify({
                'success': False,
                'message': 'Invalid verification code'
            }), 400
        
        # Enable MFA for user
        mfa_data = mfa_service.enable_mfa(user_id, secret)
        
        # Generate backup codes
        backup_codes = mfa_service.generate_backup_codes(user_id)
        
        # Log successful MFA setup
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_SETUP_COMPLETED", 
            {"backup_codes_count": len(backup_codes)}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'MFA enabled successfully',
            'backup_codes': backup_codes,
            'backup_codes_warning': 'Save these backup codes in a secure location. You can only view them once!'
        }), 200
    
    except Exception as e:
        print(f"Error verifying MFA setup: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/verify', methods=['POST'])
@token_required
def verify_mfa():
    """Verify MFA token during login"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        # Verify MFA token
        if not mfa_service.verify_user_mfa(user_id, token):
            return jsonify({
                'success': False,
                'message': 'Invalid verification code'
            }), 400
        
        # Log successful MFA verification
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_VERIFICATION_SUCCESS", 
            {"method": "totp"}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'MFA verification successful'
        }), 200
    
    except Exception as e:
        print(f"Error verifying MFA: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/backup-verify', methods=['POST'])
@token_required
def verify_backup_code():
    """Verify backup code for MFA"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        backup_code = data.get('backup_code')
        
        if not backup_code:
            return jsonify({
                'success': False,
                'message': 'Backup code is required'
            }), 400
        
        # Verify backup code
        if not mfa_service.verify_backup_code(user_id, backup_code):
            return jsonify({
                'success': False,
                'message': 'Invalid backup code'
            }), 400
        
        # Log successful backup code usage
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_BACKUP_CODE_USED", 
            {"remaining_codes": mfa_service.get_remaining_backup_codes(user_id)}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'Backup code verified successfully',
            'remaining_codes': mfa_service.get_remaining_backup_codes(user_id)
        }), 200
    
    except Exception as e:
        print(f"Error verifying backup code: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/status', methods=['GET'])
@token_required
def get_mfa_status():
    """Get MFA status for current user"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        status = mfa_service.get_mfa_status(user_id)
        
        return jsonify({
            'success': True,
            'mfa_status': status
        }), 200
    
    except Exception as e:
        print(f"Error getting MFA status: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/disable', methods=['POST'])
@token_required
def disable_mfa():
    """Disable MFA for user"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        token = data.get('token')  # Require current MFA token to disable
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Current verification code is required to disable MFA'
            }), 400
        
        # Verify current MFA token
        if not mfa_service.verify_user_mfa(user_id, token):
            return jsonify({
                'success': False,
                'message': 'Invalid verification code'
            }), 400
        
        # Disable MFA
        success = mfa_service.disable_mfa(user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to disable MFA'
            }), 500
        
        # Log MFA disable
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_DISABLED", 
            {}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'MFA disabled successfully'
        }), 200
    
    except Exception as e:
        print(f"Error disabling MFA: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@mfa_bp.route('/api/mfa/regenerate-backup-codes', methods=['POST'])
@token_required
def regenerate_backup_codes():
    """Regenerate backup codes for user"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        token = data.get('token')  # Require current MFA token
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Current verification code is required'
            }), 400
        
        # Verify current MFA token
        if not mfa_service.verify_user_mfa(user_id, token):
            return jsonify({
                'success': False,
                'message': 'Invalid verification code'
            }), 400
        
        # Regenerate backup codes
        new_backup_codes = mfa_service.regenerate_backup_codes(user_id)
        
        # Log backup codes regeneration
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        AuditLog.log_action(
            user_id, 
            "MFA_BACKUP_CODES_REGENERATED", 
            {"new_codes_count": len(new_backup_codes)}, 
            client_ip
        )
        
        return jsonify({
            'success': True,
            'message': 'Backup codes regenerated successfully',
            'backup_codes': new_backup_codes,
            'backup_codes_warning': 'Save these new backup codes in a secure location. Old backup codes are no longer valid.'
        }), 200
    
    except Exception as e:
        print(f"Error regenerating backup codes: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
