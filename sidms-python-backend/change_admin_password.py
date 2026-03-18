#!/usr/bin/env python3
"""
Script to change the hardcoded admin password in auth_service.py
Run this script to update the admin credentials for security
"""

import os
import re
import sys
from pathlib import Path

def change_admin_password(new_username=None, new_password=None):
    """
    Change the hardcoded admin credentials in auth_service.py
    
    Args:
        new_username (str): New admin username (optional)
        new_password (str): New admin password (required)
    """
    
    if not new_password:
        print("❌ Error: New password is required")
        return False
    
    # Path to auth_service.py
    auth_service_path = Path(__file__).parent / "services" / "auth_service.py"
    
    if not auth_service_path.exists():
        print(f"❌ Error: {auth_service_path} not found")
        return False
    
    try:
        # Read the current file
        with open(auth_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        backup_path = auth_service_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_path}")
        
        # Update the hardcoded credentials
        updated_content = content
        
        if new_username:
            # Replace username
            username_pattern = r'username == "iaccloudadmin"'
            updated_content = re.sub(
                username_pattern,
                f'username == "{new_username}"',
                updated_content
            )
            
            # Replace username in admin object creation
            username_obj_pattern = r"'username': 'iaccloudadmin'"
            updated_content = re.sub(
                username_obj_pattern,
                f"'username': '{new_username}'",
                updated_content
            )
        
        # Replace password
        password_pattern = r'password == "iaccloud@567"'
        updated_content = re.sub(
            password_pattern,
            f'password == "{new_password}"',
            updated_content
        )
        
        # Write updated content
        with open(auth_service_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Admin credentials updated successfully!")
        if new_username:
            print(f"   New Username: {new_username}")
        print(f"   New Password: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin credentials: {e}")
        return False

def main():
    print("🔐 SIDMS Admin Password Change Tool")
    print("=" * 40)
    
    # Get new credentials from user input
    print("\nCurrent credentials:")
    print("  Username: iaccloudadmin")
    print("  Password: iaccloud@567")
    
    print("\nEnter new credentials:")
    
    new_username = input("New username (press Enter to keep 'iaccloudadmin'): ").strip()
    if not new_username:
        new_username = "iaccloudadmin"
    
    new_password = input("New password: ").strip()
    if not new_password:
        print("❌ Password cannot be empty")
        return
    
    confirm_password = input("Confirm new password: ").strip()
    if new_password != confirm_password:
        print("❌ Passwords do not match")
        return
    
    # Validate password strength
    if len(new_password) < 8:
        print("⚠️  Warning: Password should be at least 8 characters long")
    
    # Change the credentials
    success = change_admin_password(new_username, new_password)
    
    if success:
        print("\n✅ Admin credentials changed successfully!")
        print("📝 Please remember to update your SETUP_GUIDE.md with the new credentials")
        print("🔄 Restart your backend server for changes to take effect")
    else:
        print("\n❌ Failed to change admin credentials")

if __name__ == "__main__":
    main()
