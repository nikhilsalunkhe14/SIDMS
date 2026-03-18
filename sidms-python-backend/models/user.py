from datetime import datetime
from bson import ObjectId
import bcrypt
from config.database import db

class User:
    def __init__(self, username, email, password, role="ROLE_MEMBER", enabled=False, mfa_enabled=True):
        self.username = username
        self.email = email
        self.password = self._hash_password(password)
        self.role = role
        self.enabled = enabled
        self.mfa_enabled = mfa_enabled
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "enabled": self.enabled,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def find_by_username(username):
        user_data = db.users.find_one({"username": username})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    @staticmethod
    def find_by_email(email):
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    @staticmethod
    def find_all():
        users = []
        for user_data in db.users.find():
            users.append(User.from_dict(user_data))
        return users
    
    @staticmethod
    def find_by_id(user_id):
        print(f"User.find_by_id called with: {user_id}")  # Debug line
        try:
            print(f"Converting to ObjectId: {user_id}")  # Debug line
            obj_id = ObjectId(user_id)
            print(f"ObjectId created: {obj_id}")  # Debug line
            user_data = db.users.find_one({"_id": obj_id})
            print(f"MongoDB query result: {user_data}")  # Debug line
            if user_data:
                print(f"Creating User object from data")  # Debug line
                return User.from_dict(user_data)
        except Exception as e:
            print(f"Error in find_by_id: {e}")  # Debug line
        return None
    
    @staticmethod
    def from_dict(data):
        user = User.__new__(User)
        user.username = data.get("username")
        user.email = data.get("email")
        user.password = data.get("password")
        user.role = data.get("role", "ROLE_MEMBER")
        user.enabled = data.get("enabled", False)
        user.mfa_enabled = data.get("mfa_enabled", True)
        user.created_at = data.get("created_at")
        user.updated_at = data.get("updated_at")
        user.id = str(data.get("_id"))
        return user
    
    def save(self):
        user_dict = self.to_dict()
        print(f"Saving user dict: {user_dict}")  # Debug line
        result = db.users.insert_one(user_dict)
        self.id = str(result.inserted_id)
        print(f"User saved with MongoDB ID: {self.id}")  # Debug line
        return self.id
    
    def update(self, **kwargs):
        kwargs["updated_at"] = datetime.utcnow()
        db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": kwargs}
        )
    
    def enable(self):
        self.enabled = True
        self.update(enabled=True)
    
    def disable(self):
        self.enabled = False
        self.update(enabled=False)
