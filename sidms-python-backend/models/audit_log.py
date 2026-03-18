from datetime import datetime
from bson import ObjectId
from config.database import db

class AuditLog:
    def __init__(self, user_id, action, details=None, ip_address=None):
        self.user_id = user_id
        self.action = action
        self.details = details
        self.ip_address = ip_address
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": str(ObjectId()),
            "user_id": self.user_id,
            "user_name": getattr(self, 'user_name', None),
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def log_action(user_id, action, details=None, ip_address=None, user_name=None):
        audit_log = AuditLog(user_id, action, details, ip_address)
        if user_name:
            audit_log.user_name = user_name
        audit_log.save()
    
    @staticmethod
    def log_profile_view(user_id, profile_id, ip_address=None):
        """Log when someone views a profile"""
        details = {
            "profile_id": profile_id,
            "action_type": "PROFILE_VIEW",
            "description": f"User {user_id} viewed profile {profile_id}"
        }
        AuditLog.log_action(user_id, "PROFILE_VIEW", details, ip_address)
    
    @staticmethod
    def log_profile_update(user_id, profile_id, changed_fields, ip_address=None):
        """Log when someone updates a profile"""
        details = {
            "profile_id": profile_id,
            "action_type": "PROFILE_UPDATE",
            "changed_fields": changed_fields,
            "description": f"User {user_id} updated profile {profile_id}"
        }
        AuditLog.log_action(user_id, "PROFILE_UPDATE", details, ip_address)
    
    @staticmethod
    def log_profile_create(user_id, profile_id, ip_address=None):
        """Log when someone creates a profile"""
        details = {
            "profile_id": profile_id,
            "action_type": "PROFILE_CREATE",
            "description": f"User {user_id} created profile {profile_id}"
        }
        AuditLog.log_action(user_id, "PROFILE_CREATE", details, ip_address)
    
    @staticmethod
    def log_login_attempt(username, success, ip_address=None, user_id=None):
        """Log login attempts (both successful and failed)"""
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        details = {
            "username": username,
            "action_type": "LOGIN_ATTEMPT",
            "success": success,
            "user_id": user_id
        }
        AuditLog.log_action(user_id or "anonymous", action, details, ip_address)
    
    @staticmethod
    def log_admin_action(admin_user_id, action, target_user_id=None, details=None, ip_address=None):
        """Log admin-specific actions"""
        log_details = {
            "action_type": "ADMIN_ACTION",
            "target_user_id": target_user_id,
            "admin_action": action,
            "description": f"Admin {admin_user_id} performed {action}" + (f" on user {target_user_id}" if target_user_id else "")
        }
        if details:
            log_details.update(details)
        AuditLog.log_action(admin_user_id, f"ADMIN_{action}", log_details, ip_address)
    
    @staticmethod
    def log_data_access(user_id, data_type, record_id, ip_address=None):
        """Log access to sensitive data"""
        details = {
            "data_type": data_type,
            "record_id": record_id,
            "action_type": "DATA_ACCESS",
            "description": f"User {user_id} accessed {data_type} record {record_id}"
        }
        AuditLog.log_action(user_id, "DATA_ACCESS", details, ip_address)
    
    @staticmethod
    def find_by_user_id(user_id, limit=50):
        logs = []
        for log_data in db.audit_logs.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit):
            logs.append(AuditLog.from_dict(log_data))
        return logs
    
    @staticmethod
    def find_all(limit=100):
        logs = []
        for log_data in db.audit_logs.find().sort("timestamp", -1).limit(limit):
            logs.append(AuditLog.from_dict(log_data))
        return logs
    
    @staticmethod
    def from_dict(data):
        log = AuditLog.__new__(AuditLog)
        log.user_id = data.get("user_id")
        log.action = data.get("action")
        log.details = data.get("details")
        log.ip_address = data.get("ip_address")
        log.timestamp = data.get("timestamp")
        log.id = str(data.get("_id"))
        return log
    
    def save(self):
        log_dict = self.to_dict()
        result = db.audit_logs.insert_one(log_dict)
        self.id = str(result.inserted_id)
        return self.id
