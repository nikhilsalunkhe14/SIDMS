import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from utils.key_manager import key_manager

class EncryptionService:
    """AES-256 encryption service for sensitive data with secure key management"""
    
    def __init__(self):
        self.key = key_manager.get_current_key()
        self.cipher_suite = Fernet(self.key)
    
    def refresh_key(self):
        """Refresh encryption key (useful after key rotation)"""
        self.key = key_manager.get_current_key()
        self.cipher_suite = Fernet(self.key)
        print("� Encryption key refreshed")
    
    def encrypt_field(self, data):
        """Encrypt a single field"""
        if data is None or data == "":
            return data
        
        try:
            # Convert to string if not already
            if not isinstance(data, str):
                data = str(data)
            
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            # Return as base64 string for storage
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"🔐 Encryption error: {e}")
            return data  # Fallback to original data
    
    def decrypt_field(self, encrypted_data):
        """Decrypt a single field"""
        if encrypted_data is None or encrypted_data == "":
            return encrypted_data
        
        try:
            # Check if data is encrypted (base64 format)
            if not isinstance(encrypted_data, str) or not self._is_encrypted(encrypted_data):
                return encrypted_data  # Return as-is if not encrypted
            
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"🔐 Decryption error: {e}")
            return encrypted_data  # Fallback to original data
    
    def encrypt_dict_fields(self, data_dict, fields_to_encrypt):
        """Encrypt specific fields in a dictionary"""
        if not isinstance(data_dict, dict):
            return data_dict
        
        encrypted_dict = data_dict.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_dict:
                encrypted_dict[field] = self.encrypt_field(encrypted_dict[field])
        
        return encrypted_dict
    
    def decrypt_dict_fields(self, data_dict, fields_to_decrypt):
        """Decrypt specific fields in a dictionary"""
        if not isinstance(data_dict, dict):
            return data_dict
        
        decrypted_dict = data_dict.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_dict:
                decrypted_dict[field] = self.decrypt_field(decrypted_dict[field])
        
        return decrypted_dict
    
    def _is_encrypted(self, data):
        """Check if data is encrypted (base64 format check)"""
        try:
            # Try to decode as base64
            decoded = base64.urlsafe_b64decode(data.encode())
            # Check if it's valid encrypted data (Fernet format)
            return len(decoded) > 0 and isinstance(decoded, bytes)
        except:
            return False
    
    def get_key_info(self):
        """Get information about current encryption key"""
        return key_manager.get_key_info()
    
    @staticmethod
    def get_sensitive_fields():
        """List of fields that should be encrypted"""
        return [
            'full_name',
            'email', 
            'phone_number',
            'address',
            'student_id',
            'government_id',
            'degree',
            'resume_url'
        ]

# Global encryption service instance
encryption_service = EncryptionService()
