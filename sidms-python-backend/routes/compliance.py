#!/usr/bin/env python3
"""
Compliance routes for SIDMS - GDPR and Data Protection
"""

from flask import Blueprint, request, jsonify, send_file
from middleware.auth import token_required, token_required_admin
from utils.compliance_service import compliance_service
from models.audit_log import AuditLog
from datetime import datetime
import json
import io

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/api/compliance/retention-policies', methods=['GET'])
@token_required_admin
def get_retention_policies():
    """Get all data retention policies"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        policies = compliance_service.get_retention_policies()
        
        return jsonify({
            'success': True,
            'policies': policies
        }), 200
    
    except Exception as e:
        print(f"Error getting retention policies: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/retention-policies', methods=['POST'])
@token_required_admin
def update_retention_policy():
    """Update a specific retention policy"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        data = request.get_json()
        data_type = data.get('data_type')
        policy = data.get('policy')
        
        if not data_type or not policy:
            return jsonify({
                'success': False,
                'message': 'Data type and policy are required'
            }), 400
        
        success = compliance_service.update_retention_policy(data_type, policy)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Retention policy updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update retention policy'
            }), 500
    
    except Exception as e:
        print(f"Error updating retention policy: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/consent', methods=['POST'])
@token_required
def record_consent():
    """Record user consent for data processing"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        consent_type = data.get('consent_type')
        consent_given = data.get('consent_given')
        details = data.get('details', {})
        
        if consent_type is None or consent_given is None:
            return jsonify({
                'success': False,
                'message': 'Consent type and consent given are required'
            }), 400
        
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        success = compliance_service.record_consent(
            user_id, consent_type, consent_given, client_ip, details
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Consent recorded successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to record consent'
            }), 500
    
    except Exception as e:
        print(f"Error recording consent: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/consent', methods=['GET'])
@token_required
def get_user_consents():
    """Get all consent records for current user"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        consents = compliance_service.get_user_consents(user_id)
        
        return jsonify({
            'success': True,
            'consents': consents
        }), 200
    
    except Exception as e:
        print(f"Error getting user consents: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/data-request', methods=['POST'])
@token_required
def create_data_subject_request():
    """Create a data subject request (access, portability, deletion)"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        request_type = data.get('request_type')
        details = data.get('details', {})
        
        if not request_type:
            return jsonify({
                'success': False,
                'message': 'Request type is required'
            }), 400
        
        valid_types = ['access', 'portability', 'deletion', 'correction']
        if request_type not in valid_types:
            return jsonify({
                'success': False,
                'message': f'Invalid request type. Must be one of: {valid_types}'
            }), 400
        
        request_id = compliance_service.create_data_subject_request(
            user_id, request_type, details
        )
        
        if request_id:
            return jsonify({
                'success': True,
                'message': 'Data subject request created successfully',
                'request_id': request_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create data subject request'
            }), 500
    
    except Exception as e:
        print(f"Error creating data subject request: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/data-requests', methods=['GET'])
@token_required
def get_data_subject_requests():
    """Get data subject requests (admin can see all, users see own)"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Admin can see all requests, users see only their own
        filter_user_id = None if user_role == 'ROLE_ADMIN' else user_id
        
        requests = compliance_service.get_data_subject_requests(filter_user_id)
        
        return jsonify({
            'success': True,
            'requests': requests
        }), 200
    
    except Exception as e:
        print(f"Error getting data subject requests: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/data-requests/<request_id>/process', methods=['POST'])
@token_required_admin
def process_data_subject_request(request_id):
    """Process a data subject request (admin only)"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        data = request.get_json()
        status = data.get('status')
        notes = data.get('notes', '')
        
        valid_statuses = ['pending', 'processing', 'completed', 'rejected']
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        success = compliance_service.process_data_subject_request(
            request_id, user_id, status, notes
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data subject request processed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to process data subject request'
            }), 500
    
    except Exception as e:
        print(f"Error processing data subject request: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/export-data', methods=['GET'])
@token_required
def export_user_data():
    """Export all user data in GDPR-compliant format"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        # Users can only export their own data, admins can export any
        target_user_id = request.args.get('user_id', user_id)
        
        # Only admins can export other users' data
        if target_user_id != user_id and user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        export_data = compliance_service.export_user_data(target_user_id)
        
        if not export_data:
            return jsonify({
                'success': False,
                'message': 'No data found for user'
            }), 404
        
        # Create JSON file
        json_data = json.dumps(export_data, indent=2, default=str)
        
        # Create file-like object
        output = io.BytesIO()
        output.write(json_data.encode('utf-8'))
        output.seek(0)
        
        filename = f"user_data_export_{target_user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
    
    except Exception as e:
        print(f"Error exporting user data: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/delete-data', methods=['POST'])
@token_required
def delete_user_data():
    """Delete user data in GDPR-compliant manner"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        data = request.get_json()
        target_user_id = data.get('user_id', user_id)
        reason = data.get('reason', 'User request')
        
        # Users can only delete their own data, admins can delete any
        if target_user_id != user_id and user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        success = compliance_service.delete_user_data(target_user_id, reason, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'User data deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete user data'
            }), 500
    
    except Exception as e:
        print(f"Error deleting user data: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/report', methods=['GET'])
@token_required_admin
def get_compliance_report():
    """Generate comprehensive compliance report (admin only)"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        report = compliance_service.get_compliance_report()
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        print(f"Error generating compliance report: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@compliance_bp.route('/api/compliance/cleanup', methods=['POST'])
@token_required_admin
def run_retention_cleanup():
    """Run automated data retention cleanup (admin only)"""
    try:
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if not user_id or user_role != 'ROLE_ADMIN':
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        results = compliance_service.run_retention_cleanup()
        
        return jsonify({
            'success': True,
            'message': 'Retention cleanup completed',
            'results': results
        }), 200
    
    except Exception as e:
        print(f"Error running retention cleanup: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
