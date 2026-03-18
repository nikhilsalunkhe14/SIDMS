#!/usr/bin/env python3
"""
SIDMS Auto-Deploy to Render Script
This script automates the entire Render deployment process
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Node.js
    success, _, _ = run_command("node --version")
    if not success:
        print("❌ Node.js is not installed. Please install Node.js 18+")
        return False
    print("✅ Node.js found")
    
    # Check npm
    success, _, _ = run_command("npm --version")
    if not success:
        print("❌ npm is not installed")
        return False
    print("✅ npm found")
    
    # Check Python
    success, _, _ = run_command("python --version")
    if not success:
        print("❌ Python is not installed. Please install Python 3.10+")
        return False
    print("✅ Python found")
    
    # Check Git
    success, _, _ = run_command("git --version")
    if not success:
        print("⚠️  Git not found. Install Git for deployment")
        return False
    print("✅ Git found")
    
    return True

def prepare_project():
    """Prepare project for deployment"""
    print("\n📦 Preparing project...")
    
    # Change admin password
    print("🔐 Checking admin credentials...")
    auth_service_path = Path("sidms-python-backend/services/auth_service.py")
    if auth_service_path.exists():
        with open(auth_service_path, 'r') as f:
            content = f.read()
        
        if 'iaccloudadmin' in content and 'iaccloud@567' in content:
            print("⚠️  Default admin credentials detected!")
            response = input("   Change admin password now? (y/N): ").strip().lower()
            if response == 'y':
                print("   Running password change script...")
                success, _, error = run_command("python sidms-python-backend/change_admin_password.py")
                if success:
                    print("✅ Admin password changed successfully!")
                else:
                    print(f"❌ Failed to change password: {error}")
                    return False
    
    # Prepare frontend
    print("📱 Preparing frontend...")
    frontend_path = Path("sidms-frontend")
    if frontend_path.exists():
        print("   Installing frontend dependencies...")
        success, _, error = run_command("npm install", cwd=frontend_path)
        if not success:
            print(f"❌ Failed to install frontend dependencies: {error}")
            return False
        
        print("   Building frontend...")
        success, _, error = run_command("npm run build", cwd=frontend_path)
        if not success:
            print(f"❌ Failed to build frontend: {error}")
            return False
        
        print("✅ Frontend prepared successfully")
    else:
        print("❌ Frontend directory not found")
        return False
    
    return True

def commit_and_push():
    """Commit and push changes to GitHub"""
    print("\n📝 Committing and pushing changes...")
    
    # Add all files
    success, _, error = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {error}")
        return False
    
    # Check if there are changes to commit
    success, output, _ = run_command("git status --porcelain")
    if not output.strip():
        print("✅ No changes to commit")
        return True
    
    # Commit changes
    commit_message = "Auto-deploy: Prepare for Render deployment"
    print(f"   Committing changes: {commit_message}")
    success, _, error = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    
    # Push changes
    print("   Pushing to GitHub...")
    success, _, error = run_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {error}")
        return False
    
    print("✅ Changes pushed to GitHub successfully")
    return True

def provide_render_instructions():
    """Provide clear instructions for Render setup"""
    print("\n🌐 Render Setup Instructions")
    print("=" * 50)
    
    print("\n📋 Step 1: Go to Render Dashboard")
    print("   URL: https://dashboard.render.com")
    print("   Login to your account")
    
    print("\n📋 Step 2: Create New Web Service")
    print("   1. Click 'New +' → 'Web Service'")
    print("   2. Select 'Build and deploy from a Git repository'")
    print("   3. Connect your GitHub account")
    print("   4. Select repository: nikhilsalunkhe14/SIDMS")
    
    print("\n📋 Step 3: Configure Services")
    print("   Render will automatically detect your render.yaml")
    print("   It will create TWO services:")
    print("   📱 Frontend: sidms-frontend")
    print("   🐍 Backend: sidms-backend")
    
    print("\n📋 Step 4: Set Environment Variables")
    print("   For FRONTEND service:")
    print("   - Name: REACT_APP_API_URL")
    print("   - Value: https://sidms-backend.onrender.com/api")
    print("   ")
    print("   For BACKEND service:")
    print("   - Name: MONGODB_URI")
    print("   - Value: mongodb+srv://username:password@cluster.mongodb.net/sidms")
    print("   - Name: JWT_SECRET_KEY")
    print("   - Value: your-super-secret-jwt-key-here-min-32-chars")
    print("   - Name: ENCRYPTION_KEY")
    print("   - Value: your-32-byte-encryption-key-here-very-secure")
    
    print("\n📋 Step 5: Deploy!")
    print("   Click 'Create Web Service'")
    print("   Wait for deployment to complete")
    print("   Your apps will be live at:")
    print("   🌐 Frontend: https://sidms-frontend.onrender.com")
    print("   🔗 Backend: https://sidms-backend.onrender.com")
    
    print("\n⏱️  Deployment Time: 5-10 minutes")
    print("   Monitor progress in Render dashboard")
    
    return True

def create_quick_reference():
    """Create a quick reference file"""
    reference_content = """# Quick Render Deployment Reference

## Important URLs
- Render Dashboard: https://dashboard.render.com
- Repository: https://github.com/nikhilsalunkhe14/SIDMS

## Environment Variables

### Frontend Service (sidms-frontend)
```
REACT_APP_API_URL=https://sidms-backend.onrender.com/api
```

### Backend Service (sidms-backend)
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sidms
JWT_SECRET_KEY=your-super-secret-jwt-key-here-min-32-chars
JWT_ACCESS_TOKEN_EXPIRES_IN=3600
ENCRYPTION_KEY=your-32-byte-encryption-key-here-very-secure
```

## Expected URLs After Deployment
- Frontend: https://sidms-frontend.onrender.com
- Backend: https://sidms-backend.onrender.com
- API Health: https://sidms-backend.onrender.com/health

## Testing Commands
```bash
# Test backend health
curl https://sidms-backend.onrender.com/health

# Test frontend
open https://sidms-frontend.onrender.com
```
"""
    
    with open("QUICK_RENDER_REFERENCE.md", "w", encoding='utf-8') as f:
        f.write(reference_content)
    
    print("\nCreated: QUICK_RENDER_REFERENCE.md")
    return True

def main():
    """Main auto-deployment function"""
    print("🚀 SIDMS Auto-Deploy to Render")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        return
    
    # Prepare project
    if not prepare_project():
        print("\n❌ Project preparation failed.")
        return
    
    # Commit and push
    if not commit_and_push():
        print("\n❌ Git operations failed.")
        return
    
    # Create quick reference
    create_quick_reference()
    
    # Provide instructions
    provide_render_instructions()
    
    print("\n🎉 Auto-deployment preparation completed!")
    print("\n📁 Files Created:")
    print("   ✅ QUICK_RENDER_REFERENCE.md - Quick setup guide")
    print("   ✅ render.yaml - Render configuration")
    print("   ✅ Changes pushed to GitHub")
    
    print("\n⏭ Next Steps:")
    print("   1. Follow the Render setup instructions above")
    print("   2. Your apps will auto-deploy from GitHub")
    print("   3. Configure environment variables")
    print("   4. Test your deployed applications")
    
    # Ask if user wants to open Render dashboard
    response = input("\n🌐 Open Render dashboard in browser? (y/N): ").strip().lower()
    if response == 'y':
        try:
            webbrowser.open("https://dashboard.render.com")
            print("✅ Render dashboard opened in browser")
        except:
            print("⚠️  Could not open browser automatically")
            print("   Please visit: https://dashboard.render.com")

if __name__ == "__main__":
    main()
