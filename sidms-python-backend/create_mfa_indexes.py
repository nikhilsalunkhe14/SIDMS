#!/usr/bin/env python3
"""
Create indexes for MFA collections
"""

from config.database import db

def create_mfa_indexes():
    """Create indexes for MFA collections"""
    
    # Create index for user_mfa collection
    try:
        db.user_mfa.create_index("user_id", unique=True)
        print("✅ Created index on user_mfa.user_id")
        
        db.user_mfa.create_index("enabled")
        print("✅ Created index on user_mfa.enabled")
        
        print("✅ MFA database indexes created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating MFA indexes: {e}")

if __name__ == "__main__":
    create_mfa_indexes()
