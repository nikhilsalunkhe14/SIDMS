from models.otp import OTP
from models.user import User
from services.email_service import EmailService
from models.audit_log import AuditLog

class OTPService:
    def __init__(self):
        self.email_service = EmailService()
    
    def generate_and_send_otp(self, username):
        try:
            # Find user
            user = User.find_by_username(username)
            if not user:
                return {"success": False, "message": "User not found"}
            
            if not user.enabled:
                return {"success": False, "message": "Account is not enabled"}
            
            # Clean up expired OTPs
            OTP.cleanup_expired()
            
            # Generate new OTP
            otp = OTP(user.id)
            otp.save()
            
            # Send OTP via email
            if self.email_service.send_otp_email(user.email, otp.otp_code):
                AuditLog.log_action(
                    user.id, 
                    "OTP_GENERATED", 
                    f"OTP sent to {user.email}"
                )
                return {"success": True, "message": "OTP sent to your email"}
            else:
                return {"success": False, "message": "Failed to send OTP"}
                
        except Exception as e:
            print(f"OTP generation error: {e}")
            return {"success": False, "message": "Internal server error"}
    
    def verify_otp(self, username, otp_code):
        try:
            # Find user
            user = User.find_by_username(username)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Find latest OTP for user
            otp = OTP.find_latest_by_user_id(user.id)
            if not otp:
                return {"success": False, "message": "No OTP found"}
            
            # Verify OTP
            if otp.is_valid(otp_code):
                otp.mark_as_used()
                AuditLog.log_action(
                    user.id,
                    "OTP_VERIFIED",
                    "OTP verification successful"
                )
                return {"success": True, "message": "OTP verified successfully"}
            elif otp.is_expired():
                return {"success": False, "message": "OTP has expired"}
            else:
                return {"success": False, "message": "Invalid OTP"}
                
        except Exception as e:
            print(f"OTP verification error: {e}")
            return {"success": False, "message": "Internal server error"}
