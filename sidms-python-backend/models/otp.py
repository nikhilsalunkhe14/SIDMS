from datetime import datetime, timedelta
from bson import ObjectId
import secrets
from config.database import db

class OTP:
    def __init__(self, user_id, otp_code=None, expiry_time=None):
        self.user_id = user_id
        self.otp_code = otp_code or self._generate_otp()
        self.expiry_time = expiry_time or (datetime.utcnow() + timedelta(minutes=5))
        self.created_at = datetime.utcnow()
        self.is_used = False
    
    def _generate_otp(self):
        return str(secrets.randbelow(1000000)).zfill(6)
    
    def is_expired(self):
        return datetime.utcnow() > self.expiry_time
    
    def is_valid(self, otp_code):
        return not self.is_expired() and not self.is_used and self.otp_code == otp_code
    
    def to_dict(self):
        return {
            "_id": str(ObjectId()),
            "user_id": self.user_id,
            "otp_code": self.otp_code,
            "expiry_time": self.expiry_time,
            "created_at": self.created_at,
            "is_used": self.is_used
        }
    
    @staticmethod
    def find_latest_by_user_id(user_id):
        otp_data = db.otps.find_one(
            {"user_id": user_id, "is_used": False},
            sort=[("created_at", -1)]
        )
        if otp_data:
            return OTP.from_dict(otp_data)
        return None
    
    @staticmethod
    def from_dict(data):
        otp = OTP.__new__(OTP)
        otp.user_id = data.get("user_id")
        otp.otp_code = data.get("otp_code")
        otp.expiry_time = data.get("expiry_time")
        otp.created_at = data.get("created_at")
        otp.is_used = data.get("is_used", False)
        otp.id = str(data.get("_id"))
        return otp
    
    def save(self):
        otp_dict = self.to_dict()
        result = db.otps.insert_one(otp_dict)
        self.id = str(result.inserted_id)
        return self.id
    
    def mark_as_used(self):
        self.is_used = True
        db.otps.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"is_used": True}}
        )
    
    @staticmethod
    def cleanup_expired():
        """Remove expired OTPs"""
        db.otps.delete_many({
            "expiry_time": {"$lt": datetime.utcnow()}
        })
