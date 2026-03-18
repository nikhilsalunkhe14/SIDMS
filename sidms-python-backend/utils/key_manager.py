#!/usr/bin/env python3
"""
Secure Key Management System for SIDMS
Handles encryption key generation, storage, and rotation
"""

import os
import base64
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from pathlib import Path

class KeyManager:
    """Secure key management for encryption operations"""
    
    def __init__(self):
        self.keys_dir = Path("keys")
        self.keys_dir.mkdir(exist_ok=True)
        self.current_key_file = self.keys_dir / "current_key.json"
        self.key_history_file = self.keys_dir / "key_history.json"
        self._initialize_key_system()
    
    def _initialize_key_system(self):
        """Initialize the key management system"""
        # Try to get key from environment first (production)
        env_key = os.getenv('ENCRYPTION_KEY')
        if env_key:
            print("🔑 Using encryption key from environment")
            self.current_key = base64.urlsafe_b64decode(env_key.encode())
            return
        
        # Try to load existing key from file
        if self.current_key_file.exists():
            print("🔑 Loading encryption key from file")
            self.current_key = self._load_current_key()
            return
        
        # Generate new key if none exists
        print("🔑 Generating new encryption key")
        self.current_key = self._generate_new_key()
        self._save_current_key()
        self._add_to_history("generated")
        
        print(f"🔐 New encryption key: {base64.urlsafe_b64encode(self.current_key).decode()}")
        print("⚠️  Set ENCRYPTION_KEY environment variable in production!")
    
    def _generate_new_key(self):
        """Generate a new encryption key"""
        return Fernet.generate_key()
    
    def _save_current_key(self):
        """Save current key to file with metadata"""
        key_data = {
            "key": base64.urlsafe_b64encode(self.current_key).decode(),
            "created_at": datetime.utcnow().isoformat(),
            "version": self._get_next_version(),
            "status": "active"
        }
        
        with open(self.current_key_file, 'w') as f:
            json.dump(key_data, f, indent=2)
    
    def _load_current_key(self):
        """Load current key from file"""
        with open(self.current_key_file, 'r') as f:
            key_data = json.load(f)
        
        return base64.urlsafe_b64decode(key_data['key'].encode())
    
    def _add_to_history(self, action, old_key=None, new_key=None):
        """Add key operation to history"""
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "version": self._get_next_version() if action == "generated" else self._get_current_version()
        }
        
        if old_key:
            history_entry["old_key"] = base64.urlsafe_b64encode(old_key).decode()
        if new_key:
            history_entry["new_key"] = base64.urlsafe_b64encode(new_key).decode()
        
        # Load existing history
        history = []
        if self.key_history_file.exists():
            with open(self.key_history_file, 'r') as f:
                history = json.load(f)
        
        # Add new entry
        history.append(history_entry)
        
        # Save history (keep last 10 entries)
        with open(self.key_history_file, 'w') as f:
            json.dump(history[-10:], f, indent=2)
    
    def _get_current_version(self):
        """Get current key version"""
        if not self.current_key_file.exists():
            return 0
        
        with open(self.current_key_file, 'r') as f:
            key_data = json.load(f)
        
        return key_data.get('version', 1)
    
    def _get_next_version(self):
        """Get next version number"""
        return self._get_current_version() + 1
    
    def get_current_key(self):
        """Get the current encryption key"""
        return self.current_key
    
    def get_current_key_base64(self):
        """Get current key as base64 string"""
        return base64.urlsafe_b64encode(self.current_key).decode()
    
    def rotate_key(self):
        """Rotate to a new encryption key"""
        print("🔄 Starting key rotation...")
        
        old_key = self.current_key
        new_key = self._generate_new_key()
        
        # Update current key
        self.current_key = new_key
        self._save_current_key()
        self._add_to_history("rotated", old_key=old_key, new_key=new_key)
        
        print(f"🔑 Key rotated successfully!")
        print(f"📋 Old key version: {self._get_current_version() - 1}")
        print(f"📋 New key version: {self._get_current_version()}")
        
        return {
            "old_key": old_key,
            "new_key": new_key,
            "old_version": self._get_current_version() - 1,
            "new_version": self._get_current_version()
        }
    
    def backup_key(self, backup_path=None):
        """Backup current key to specified path"""
        if not backup_path:
            backup_path = f"keys/backup_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        key_data = {
            "key": base64.urlsafe_b64encode(self.current_key).decode(),
            "created_at": datetime.utcnow().isoformat(),
            "version": self._get_current_version(),
            "backup_timestamp": datetime.utcnow().isoformat(),
            "status": "backup"
        }
        
        with open(backup_path, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        print(f"📦 Key backed up to: {backup_path}")
        return backup_path
    
    def restore_key(self, backup_path):
        """Restore key from backup"""
        with open(backup_path, 'r') as f:
            key_data = json.load(f)
        
        self.current_key = base64.urlsafe_b64decode(key_data['key'].encode())
        self._save_current_key()
        self._add_to_history("restored")
        
        print(f"🔄 Key restored from backup: {backup_path}")
        return True
    
    def get_key_info(self):
        """Get information about current key"""
        return {
            "version": self._get_current_version(),
            "created_at": datetime.fromtimestamp(
                self.current_key_file.stat().st_mtime
            ).isoformat() if self.current_key_file.exists() else None,
            "key_length": len(self.current_key),
            "algorithm": "AES-256",
            "storage": "file" if not os.getenv('ENCRYPTION_KEY') else "environment"
        }
    
    def list_history(self):
        """List key operation history"""
        if not self.key_history_file.exists():
            return []
        
        with open(self.key_history_file, 'r') as f:
            return json.load(f)

# Global key manager instance
key_manager = KeyManager()
