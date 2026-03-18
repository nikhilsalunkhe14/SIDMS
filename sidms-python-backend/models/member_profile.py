from datetime import datetime
from bson import ObjectId
from utils.encryption import encryption_service
from config.database import db

class MemberProfile:
    def __init__(self, user_id, full_name, email, phone_number, residential_address, college_name, resume_url, student_id, degree=None, status="active"):
        print(f"🔐 Creating encrypted MemberProfile for: {full_name}")  # Debug line
        self.user_id = user_id
        self.status = status  # Added status field (active/inactive/archived)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Encrypt sensitive fields
        sensitive_fields = ['full_name', 'email', 'phone_number', 'residential_address', 'college_name', 'student_id', 'degree', 'resume_url']
        data_to_encrypt = {
            'full_name': full_name,
            'email': email,
            'phone_number': phone_number,
            'residential_address': residential_address,  # NEW: Separate residential address
            'college_name': college_name,              # NEW: Separate college name
            'degree': degree,
            'resume_url': resume_url,
            'student_id': student_id
        }
        
        encrypted_data = encryption_service.encrypt_dict_fields(data_to_encrypt, sensitive_fields)
        
        # Store encrypted data
        self.full_name = encrypted_data.get('full_name')
        self.email = encrypted_data.get('email')
        self.phone_number = encrypted_data.get('phone_number')
        self.residential_address = encrypted_data.get('residential_address')  # NEW
        self.college_name = encrypted_data.get('college_name')              # NEW
        self.degree = encrypted_data.get('degree')
        self.resume_url = encrypted_data.get('resume_url')
        self.student_id = encrypted_data.get('student_id')
        
        print(f"🔐 Encrypted profile data for user: {user_id}")  # Debug line
    
    def to_dict(self, decrypt=True):
        """Convert profile to dictionary, with optional decryption"""
        profile_data = {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "residential_address": self.residential_address,  # NEW
            "college_name": self.college_name,              # NEW
            "degree": self.degree,
            "student_id": self.student_id,
            "resume_url": self.resume_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Decrypt sensitive fields if requested
        if decrypt:
            sensitive_fields = ['full_name', 'email', 'phone_number', 'residential_address', 'college_name', 'student_id', 'degree', 'resume_url']
            decrypted_data = encryption_service.decrypt_dict_fields(profile_data, sensitive_fields)
            return decrypted_data
        
        return profile_data
    
    @staticmethod
    def find_by_user_id(user_id):
        profile_data = db.member_profiles.find_one({"user_id": user_id})
        if profile_data:
            print(f"DEBUG: Raw profile data from DB: {profile_data.get('full_name', 'None')[:50]}")
            profile = MemberProfile.from_dict(profile_data)
            print(f"DEBUG: Profile object full_name: {profile.full_name[:50] if profile.full_name else 'None'}")
            return profile
        return None
    
    @staticmethod
    def find_by_id(profile_id):
        profile_data = db.member_profiles.find_one({"_id": ObjectId(profile_id)})
        if profile_data:
            return MemberProfile.from_dict(profile_data)
        return None
    
    @staticmethod
    def find_all():
        profiles = []
        for profile_data in db.member_profiles.find():
            profiles.append(MemberProfile.from_dict(profile_data))
        return profiles
    
    @staticmethod
    def from_dict(data, decrypt=True):
        """Create profile from dictionary, with optional decryption"""
        profile = MemberProfile.__new__(MemberProfile)
        profile.user_id = data.get("user_id")
        profile.id = str(data.get("_id"))
        
        if decrypt:
            # Decrypt sensitive fields when creating object
            sensitive_fields = ['full_name', 'email', 'phone_number', 'residential_address', 'college_name', 'student_id', 'degree', 'resume_url']
            decrypted_data = encryption_service.decrypt_dict_fields(data, sensitive_fields)
            
            profile.full_name = decrypted_data.get("full_name")
            profile.email = decrypted_data.get("email")
            profile.phone_number = decrypted_data.get("phone_number")
            profile.residential_address = decrypted_data.get("residential_address")  # NEW
            profile.college_name = decrypted_data.get("college_name")              # NEW
            profile.degree = decrypted_data.get("degree")
            profile.student_id = decrypted_data.get("student_id")
            profile.resume_url = decrypted_data.get("resume_url")
        else:
            # Keep encrypted data (for database operations)
            profile.full_name = data.get("full_name")
            profile.email = data.get("email")
            profile.phone_number = data.get("phone_number")
            profile.residential_address = data.get("residential_address")  # NEW
            profile.college_name = data.get("college_name")              # NEW
            profile.degree = data.get("degree")
            profile.student_id = data.get("student_id")
            profile.resume_url = data.get("resume_url")
        
        profile.status = data.get("status", "active")
        profile.created_at = data.get("created_at")
        profile.updated_at = data.get("updated_at")
        return profile
    
    def save(self):
        """Save profile to database with encrypted data"""
        profile_dict = self.to_dict(decrypt=False)  # Save encrypted data
        result = db.member_profiles.insert_one(profile_dict)
        self.id = str(result.inserted_id)
        return self.id
    
    def update(self):
        """Update profile in database with encrypted data"""
        profile_dict = self.to_dict(decrypt=False)  # Save encrypted data
        profile_dict['updated_at'] = datetime.utcnow()
        db.member_profiles.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": profile_dict}
        )
    
    def archive(self):
        """Archive the profile (soft delete)"""
        self.status = "archived"
        self.updated_at = datetime.utcnow()
        db.member_profiles.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"status": "archived", "updated_at": self.updated_at}}
        )
    
    def restore(self):
        """Restore the profile from archived state"""
        self.status = "active"
        self.updated_at = datetime.utcnow()
        db.member_profiles.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"status": "active", "updated_at": self.updated_at}}
        )
    
    def delete(self):
        db.member_profiles.delete_one({"_id": ObjectId(self.id)})
    
    def to_response_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "government_id": self.government_id,
            "resume_url": self.resume_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
