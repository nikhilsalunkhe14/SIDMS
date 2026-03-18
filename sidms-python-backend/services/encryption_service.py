from cryptography.fernet import Fernet
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class EncryptionService:
    _cipher = None
    
    @classmethod
    def _get_cipher(cls):
        if cls._cipher is None:
            key = os.getenv('AES_KEY')
            if not key:
                raise ValueError("AES_KEY not found in environment variables")
            # Ensure key is properly formatted for Fernet
            key_bytes = key.encode()
            if len(key_bytes) != 44:  # Fernet key should be 44 bytes base64
                # Pad or truncate to proper length
                key_bytes = key_bytes.ljust(44, b'0')[:44]
            cls._cipher = Fernet(base64.urlsafe_b64decode(key_bytes))
        return cls._cipher
    
    @classmethod
    def encrypt(cls, data):
        if not data:
            return None
        cipher = cls._get_cipher()
        encrypted_data = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    @classmethod
    def decrypt(cls, encrypted_data):
        if not encrypted_data:
            return None
        try:
            cipher = cls._get_cipher()
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
