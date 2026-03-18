#!/usr/bin/env python3
"""
Compliance Service for SIDMS - GDPR and Data Protection Compliance
Handles data retention, user rights, consent management, and audit trails
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from config.database import db
from models.audit_log import AuditLog

class ComplianceService:
    """GDPR and Data Protection Compliance Service"""
    
    def __init__(self):
        self.compliance_dir = Path("compliance")
        self.compliance_dir.mkdir(exist_ok=True)
        self.consent_file = self.compliance_dir / "user_consents.json"
        self.retention_file = self.compliance_dir / "retention_policies.json"
        self.requests_file = self.compliance_dir / "data_subject_requests.json"
        
        # Initialize default retention policies
        self._initialize_retention_policies()
    
    def _initialize_retention_policies(self):
        """Initialize default data retention policies"""
        default_policies = {
            "user_profiles": {
                "retention_period_days": 2555,  # 7 years
                "description": "Student profiles and academic data",
                "gdpr_basis": "legitimate_interest",
                "auto_delete": True
            },
            "audit_logs": {
                "retention_period_days": 1095,  # 3 years
                "description": "System audit logs and access records",
                "gdpr_basis": "legal_obligation",
                "auto_delete": True
            },
            "user_consents": {
                "retention_period_days": 1825,  # 5 years
                "description": "User consent records and preferences",
                "gdpr_basis": "legal_obligation",
                "auto_delete": False
            },
            "backup_data": {
                "retention_period_days": 90,  # 3 months
                "description": "System backup data",
                "gdpr_basis": "legitimate_interest",
                "auto_delete": True
            },
            "temp_data": {
                "retention_period_days": 30,  # 1 month
                "description": "Temporary session and cache data",
                "gdpr_basis": "legitimate_interest",
                "auto_delete": True
            }
        }
        
        # Save default policies if file doesn't exist
        if not self.retention_file.exists():
            with open(self.retention_file, 'w') as f:
                json.dump(default_policies, f, indent=2)
    
    def get_retention_policies(self) -> Dict[str, Any]:
        """Get all data retention policies"""
        with open(self.retention_file, 'r') as f:
            return json.load(f)
    
    def update_retention_policy(self, data_type: str, policy: Dict[str, Any]) -> bool:
        """Update a specific retention policy"""
        try:
            policies = self.get_retention_policies()
            policies[data_type] = policy
            
            with open(self.retention_file, 'w') as f:
                json.dump(policies, f, indent=2)
            
            # Log policy change
            AuditLog.log_action(
                "system",
                "RETENTION_POLICY_UPDATED",
                {
                    "data_type": data_type,
                    "new_policy": policy
                }
            )
            
            return True
        except Exception as e:
            print(f"Error updating retention policy: {e}")
            return False
    
    def record_consent(self, user_id: str, consent_type: str, consent_given: bool, 
                       ip_address: str = None, details: Dict = None) -> bool:
        """Record user consent for data processing"""
        try:
            # Load existing consents
            consents = {}
            if self.consent_file.exists():
                with open(self.consent_file, 'r') as f:
                    consents = json.load(f)
            
            # Initialize user consents if not exists
            if user_id not in consents:
                consents[user_id] = {}
            
            # Record consent
            consent_record = {
                "consent_type": consent_type,
                "consent_given": consent_given,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "details": details or {},
                "version": len(consents[user_id].get(consent_type, [])) + 1
            }
            
            # Add to user's consent history
            if consent_type not in consents[user_id]:
                consents[user_id][consent_type] = []
            
            consents[user_id][consent_type].append(consent_record)
            
            # Save consents
            with open(self.consent_file, 'w') as f:
                json.dump(consents, f, indent=2)
            
            # Log consent recording
            AuditLog.log_action(
                user_id,
                "CONSENT_RECORDED",
                {
                    "consent_type": consent_type,
                    "consent_given": consent_given,
                    "version": consent_record["version"]
                },
                ip_address
            )
            
            return True
        except Exception as e:
            print(f"Error recording consent: {e}")
            return False
    
    def get_user_consents(self, user_id: str) -> Dict[str, Any]:
        """Get all consent records for a user"""
        try:
            if not self.consent_file.exists():
                return {}
            
            with open(self.consent_file, 'r') as f:
                consents = json.load(f)
            
            return consents.get(user_id, {})
        except Exception as e:
            print(f"Error getting user consents: {e}")
            return {}
    
    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given valid consent for a specific type"""
        user_consents = self.get_user_consents(user_id)
        
        if consent_type not in user_consents:
            return False
        
        # Get latest consent for this type
        consent_history = user_consents[consent_type]
        if not consent_history:
            return False
        
        latest_consent = consent_history[-1]
        return latest_consent.get("consent_given", False)
    
    def create_data_subject_request(self, user_id: str, request_type: str, 
                                  details: Dict = None) -> str:
        """Create a data subject request (access, portability, deletion)"""
        try:
            request_id = f"DSR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            request_data = {
                "request_id": request_id,
                "user_id": user_id,
                "request_type": request_type,  # access, portability, deletion, correction
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "details": details or {},
                "processed_at": None,
                "processed_by": None,
                "notes": None
            }
            
            # Load existing requests
            requests = []
            if self.requests_file.exists():
                with open(self.requests_file, 'r') as f:
                    requests = json.load(f)
            
            # Add new request
            requests.append(request_data)
            
            # Save requests
            with open(self.requests_file, 'w') as f:
                json.dump(requests, f, indent=2)
            
            # Log request creation
            AuditLog.log_action(
                user_id,
                "DATA_SUBJECT_REQUEST_CREATED",
                {
                    "request_id": request_id,
                    "request_type": request_type
                }
            )
            
            return request_id
        except Exception as e:
            print(f"Error creating data subject request: {e}")
            return None
    
    def get_data_subject_requests(self, user_id: str = None, status: str = None) -> List[Dict]:
        """Get data subject requests with optional filtering"""
        try:
            if not self.requests_file.exists():
                return []
            
            with open(self.requests_file, 'r') as f:
                requests = json.load(f)
            
            # Apply filters
            filtered_requests = requests
            if user_id:
                filtered_requests = [r for r in filtered_requests if r["user_id"] == user_id]
            
            if status:
                filtered_requests = [r for r in filtered_requests if r["status"] == status]
            
            return filtered_requests
        except Exception as e:
            print(f"Error getting data subject requests: {e}")
            return []
    
    def process_data_subject_request(self, request_id: str, processor_id: str, 
                                  status: str, notes: str = None) -> bool:
        """Process a data subject request"""
        try:
            # Load requests
            with open(self.requests_file, 'r') as f:
                requests = json.load(f)
            
            # Find and update request
            for request in requests:
                if request["request_id"] == request_id:
                    request["status"] = status
                    request["processed_at"] = datetime.utcnow().isoformat()
                    request["processed_by"] = processor_id
                    request["notes"] = notes
                    
                    # Save updated requests
                    with open(self.requests_file, 'w') as f:
                        json.dump(requests, f, indent=2)
                    
                    # Log request processing
                    AuditLog.log_action(
                        processor_id,
                        "DATA_SUBJECT_REQUEST_PROCESSED",
                        {
                            "request_id": request_id,
                            "status": status,
                            "original_user_id": request["user_id"]
                        }
                    )
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Error processing data subject request: {e}")
            return False
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data in GDPR-compliant format"""
        try:
            export_data = {
                "export_info": {
                    "user_id": user_id,
                    "export_date": datetime.utcnow().isoformat(),
                    "format": "json",
                    "version": "1.0"
                },
                "user_profile": {},
                "consents": {},
                "audit_logs": [],
                "requests": []
            }
            
            # Get user profile data
            from models.member_profile import MemberProfile
            profile = MemberProfile.find_by_user_id(user_id)
            if profile:
                export_data["user_profile"] = profile.to_dict(decrypt=True)
            
            # Get consent records
            export_data["consents"] = self.get_user_consents(user_id)
            
            # Get relevant audit logs
            user_logs = list(db.audit_logs.find(
                {"user_id": user_id},
                {"_id": 0, "timestamp": 1, "action": 1, "details": 1, "ip_address": 1}
            ).sort("timestamp", -1).limit(100))
            
            # Convert datetime to string for JSON serialization
            for log in user_logs:
                if "timestamp" in log and log["timestamp"]:
                    log["timestamp"] = log["timestamp"].isoformat()
            
            export_data["audit_logs"] = user_logs
            
            # Get data subject requests
            export_data["requests"] = self.get_data_subject_requests(user_id)
            
            # Log data export
            AuditLog.log_action(
                user_id,
                "DATA_EXPORTED",
                {
                    "export_format": "json",
                    "record_count": len(export_data["audit_logs"])
                }
            )
            
            return export_data
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return {}
    
    def delete_user_data(self, user_id: str, reason: str = None, 
                        processor_id: str = None) -> bool:
        """Delete user data in GDPR-compliant manner"""
        try:
            deletion_log = {
                "user_id": user_id,
                "deletion_date": datetime.utcnow().isoformat(),
                "reason": reason or "User request",
                "processor_id": processor_id,
                "deleted_data": []
            }
            
            # Delete user profile
            from models.member_profile import MemberProfile
            profile = MemberProfile.find_by_user_id(user_id)
            if profile:
                # Soft delete by archiving
                profile.archive()
                deletion_log["deleted_data"].append("member_profile")
            
            # Anonymize audit logs (keep for security but remove personal data)
            db.audit_logs.update_many(
                {"user_id": user_id},
                {"$set": {"user_id": f"DELETED_{datetime.utcnow().strftime('%Y%m%d')}_{hash(user_id)}"}}
            )
            deletion_log["deleted_data"].append("audit_logs_anonymized")
            
            # Log deletion
            AuditLog.log_action(
                processor_id or "system",
                "USER_DATA_DELETED",
                {
                    "target_user_id": user_id,
                    "reason": reason,
                    "deleted_items": deletion_log["deleted_data"]
                }
            )
            
            # Save deletion record
            deletion_file = self.compliance_dir / f"deletion_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(deletion_file, 'w') as f:
                json.dump(deletion_log, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "retention_policies": self.get_retention_policies(),
                "statistics": {
                    "total_consents": 0,
                    "active_requests": 0,
                    "processed_requests": 0,
                    "data_exports": 0,
                    "data_deletions": 0
                },
                "upcoming_retention": []
            }
            
            # Count consents
            if self.consent_file.exists():
                with open(self.consent_file, 'r') as f:
                    consents = json.load(f)
                report["statistics"]["total_consents"] = len(consents)
            
            # Count requests
            all_requests = self.get_data_subject_requests()
            report["statistics"]["active_requests"] = len([r for r in all_requests if r["status"] == "pending"])
            report["statistics"]["processed_requests"] = len([r for r in all_requests if r["status"] in ["completed", "rejected"]])
            
            # Count recent operations from audit logs
            recent_logs = list(db.audit_logs.find({
                "action": {"$in": ["DATA_EXPORTED", "USER_DATA_DELETED"]}
            }))
            
            report["statistics"]["data_exports"] = len([log for log in recent_logs if log["action"] == "DATA_EXPORTED"])
            report["statistics"]["data_deletions"] = len([log for log in recent_logs if log["action"] == "USER_DATA_DELETED"])
            
            return report
        except Exception as e:
            print(f"Error generating compliance report: {e}")
            return {}
    
    def run_retention_cleanup(self) -> Dict[str, int]:
        """Run automated data retention cleanup"""
        try:
            cleanup_results = {
                "deleted_profiles": 0,
                "deleted_logs": 0,
                "deleted_temp_data": 0,
                "errors": 0
            }
            
            policies = self.get_retention_policies()
            cutoff_date = datetime.utcnow()
            
            # Clean up old profiles
            if "user_profiles" in policies:
                retention_days = policies["user_profiles"]["retention_period_days"]
                cutoff = cutoff_date - timedelta(days=retention_days)
                
                old_profiles = db.member_profiles.find({
                    "updated_at": {"$lt": cutoff},
                    "status": "archived"
                })
                
                for profile in old_profiles:
                    db.member_profiles.delete_one({"_id": profile["_id"]})
                    cleanup_results["deleted_profiles"] += 1
            
            # Clean up old audit logs
            if "audit_logs" in policies:
                retention_days = policies["audit_logs"]["retention_period_days"]
                cutoff = cutoff_date - timedelta(days=retention_days)
                
                old_logs = db.audit_logs.find({
                    "timestamp": {"$lt": cutoff}
                })
                
                for log in old_logs:
                    db.audit_logs.delete_one({"_id": log["_id"]})
                    cleanup_results["deleted_logs"] += 1
            
            # Log cleanup operation
            AuditLog.log_action(
                "system",
                "RETENTION_CLEANUP_COMPLETED",
                cleanup_results
            )
            
            return cleanup_results
        except Exception as e:
            print(f"Error running retention cleanup: {e}")
            return {"errors": 1}

# Global compliance service instance
compliance_service = ComplianceService()
