#!/usr/bin/env python3
"""
Multi-Factor Authentication (MFA) Service for SIDMS
Handles TOTP generation, QR codes, and backup codes
"""

import pyotp
import qrcode
import io
import base64
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path

class MFAService:
    """Multi-Factor Authentication service using TOTP"""
    
    def __init__(self):
        self.backup_codes_dir = Path("backup_codes")
        self.backup_codes_dir.mkdir(exist_ok=True)
        self.issuer_name = "SIDMS - Secure IAC Data Management"
    
    def generate_secret(self):
        """Generate a new TOTP secret for a user"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email, secret):
        """Generate QR code for TOTP setup"""
        # Create provisioning URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'qr_code': f"data:image/png;base64,{img_str}",
            'secret': secret,
            'manual_entry_key': secret,
            'totp_uri': totp_uri
        }
    
    def verify_token(self, secret, token):
        """Verify a TOTP token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
        except Exception as e:
            print(f"MFA verification error: {e}")
            return False
    
    def generate_backup_codes(self, user_id, count=10):
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            code = f"{secrets.randbelow(1000000):06d}"
            codes.append(code)
        
        # Save backup codes to file
        backup_data = {
            'user_id': user_id,
            'codes': codes,
            'created_at': datetime.utcnow().isoformat(),
            'used': [False] * count
        }
        
        backup_file = self.backup_codes_dir / f"backup_codes_{user_id}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return codes
    
    def verify_backup_code(self, user_id, code):
        """Verify and consume a backup code"""
        backup_file = self.backup_codes_dir / f"backup_codes_{user_id}.json"
        
        if not backup_file.exists():
            return False
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Find and mark the code as used
        for i, (stored_code, used) in enumerate(zip(backup_data['codes'], backup_data['used'])):
            if not used and stored_code == code:
                backup_data['used'][i] = True
                backup_data['last_used_at'] = datetime.utcnow().isoformat()
                
                # Save updated backup data
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                return True
        
        return False
    
    def get_remaining_backup_codes(self, user_id):
        """Get count of remaining backup codes"""
        backup_file = self.backup_codes_dir / f"backup_codes_{user_id}.json"
        
        if not backup_file.exists():
            return 0
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        remaining = sum(1 for used in backup_data['used'] if not used)
        return remaining
    
    def regenerate_backup_codes(self, user_id):
        """Regenerate backup codes (invalidates old ones)"""
        return self.generate_backup_codes(user_id)
    
    def is_mfa_enabled(self, user_id):
        """Check if MFA is enabled for a user"""
        # This would typically check the database
        # For now, we'll check if user has MFA secret stored
        from config.database import db
        
        user_mfa = db.user_mfa.find_one({'user_id': user_id})
        return user_mfa is not None and user_mfa.get('enabled', False)
    
    def enable_mfa(self, user_id, secret):
        """Enable MFA for a user"""
        from config.database import db
        
        mfa_data = {
            'user_id': user_id,
            'secret': secret,
            'enabled': True,
            'enabled_at': datetime.utcnow(),
            'backup_codes_generated': False
        }
        
        # Upsert MFA configuration
        db.user_mfa.update_one(
            {'user_id': user_id},
            {'$set': mfa_data},
            upsert=True
        )
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes(user_id)
        mfa_data['backup_codes'] = backup_codes
        mfa_data['backup_codes_generated'] = True
        
        # Update with backup codes info
        db.user_mfa.update_one(
            {'user_id': user_id},
            {'$set': {'backup_codes_generated': True, 'last_backup_generation': datetime.utcnow()}}
        )
        
        return mfa_data
    
    def disable_mfa(self, user_id):
        """Disable MFA for a user"""
        from config.database import db
        
        result = db.user_mfa.update_one(
            {'user_id': user_id},
            {'$set': {'enabled': False, 'disabled_at': datetime.utcnow()}}
        )
        
        # Remove backup codes
        backup_file = self.backup_codes_dir / f"backup_codes_{user_id}.json"
        if backup_file.exists():
            backup_file.unlink()
        
        return result.modified_count > 0
    
    def get_user_mfa_secret(self, user_id):
        """Get MFA secret for a user"""
        from config.database import db
        
        user_mfa = db.user_mfa.find_one({'user_id': user_id, 'enabled': True})
        return user_mfa.get('secret') if user_mfa else None
    
    def verify_user_mfa(self, user_id, token):
        """Verify MFA token for a user"""
        secret = self.get_user_mfa_secret(user_id)
        if not secret:
            return False
        
        return self.verify_token(secret, token)
    
    def get_mfa_status(self, user_id):
        """Get MFA status for a user"""
        from config.database import db
        
        user_mfa = db.user_mfa.find_one({'user_id': user_id})
        if not user_mfa:
            return {
                'enabled': False,
                'setup_required': True
            }
        
        return {
            'enabled': user_mfa.get('enabled', False),
            'enabled_at': user_mfa.get('enabled_at'),
            'backup_codes_remaining': self.get_remaining_backup_codes(user_id),
            'last_backup_generation': user_mfa.get('last_backup_generation')
        }

# Global MFA service instance
mfa_service = MFAService()
