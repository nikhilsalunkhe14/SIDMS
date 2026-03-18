#!/usr/bin/env python3
"""
SIDMS Render Deployment Helper Script
This script helps prepare to project for Render deployment
"""

import os
import sys
import subprocess
import json
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
        print("⚠️  Git not found. Install Git for better deployment")
    else:
        print("✅ Git found")
    
    return True

def prepare_frontend():
    """Prepare frontend for deployment"""
    print("\n📦 Preparing frontend...")
    
    frontend_path = Path("sidms-frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("   Installing frontend dependencies...")
    success, _, error = run_command("npm install", cwd=frontend_path)
    if not success:
        print(f"❌ Failed to install frontend dependencies: {error}")
        return False
    
    # Build frontend
    print("   Building frontend...")
    success, _, error = run_command("npm run build", cwd=frontend_path)
    if not success:
        print(f"❌ Failed to build frontend: {error}")
        return False
    
    print("✅ Frontend prepared successfully")
    return True

def prepare_backend():
    """Prepare backend for deployment"""
    print("\n🐍 Preparing backend...")
    
    backend_path = Path("sidms-python-backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if requirements file exists
    req_file = backend_path / "requirements-vercel.txt"
    if not req_file.exists():
        print("❌ requirements-vercel.txt not found")
        return False
    
    print("✅ Backend prepared successfully")
    return True

def check_admin_credentials():
    """Check if admin credentials have been changed from defaults"""
    print("\n🔐 Checking admin credentials...")
    
    auth_service_path = Path("sidms-python-backend/services/auth_service.py")
    if not auth_service_path.exists():
        print("❌ auth_service.py not found")
        return False
    
    with open(auth_service_path, 'r') as f:
        content = f.read()
    
    # Check for default credentials
    if 'iaccloudadmin' in content and 'iaccloud@567' in content:
        print("⚠️  WARNING: Default admin credentials detected!")
        print("   Please run: python sidms-python-backend/change_admin_password.py")
        
        response = input("   Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Deployment preparation cancelled for security reasons")
            return False
    else:
        print("✅ Admin credentials appear to be customized")
    
    return True

def check_render_config():
    """Check if render.yaml exists"""
    print("\n📋 Checking Render configuration...")
    
    render_config = Path("render.yaml")
    if not render_config.exists():
        print("❌ render.yaml not found")
        return False
    
    print("✅ render.yaml found")
    return True

def prepare_git():
    """Prepare git repository for deployment"""
    print("\n📝 Preparing Git repository...")
    
    # Check if git is initialized
    git_dir = Path(".git")
    if not git_dir.exists():
        print("   Initializing Git repository...")
        success, _, error = run_command("git init")
        if not success:
            print(f"❌ Failed to initialize git: {error}")
            return False
    
    # Add all files
    print("   Adding files to Git...")
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
    print("   Committing changes...")
    success, _, error = run_command('git commit -m "Configure for Render deployment"')
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    
    print("✅ Git repository prepared")
    return True

def main():
    """Main deployment preparation function"""
    print("🚀 SIDMS Render Deployment Helper")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        return
    
    # Check admin credentials
    if not check_admin_credentials():
        return
    
    # Prepare frontend
    if not prepare_frontend():
        print("\n❌ Frontend preparation failed.")
        return
    
    # Prepare backend
    if not prepare_backend():
        print("\n❌ Backend preparation failed.")
        return
    
    # Check Render configuration
    if not check_render_config():
        print("\n❌ Render configuration not found.")
        return
    
    # Prepare git
    prepare_git()
    
    print("\n🎉 Deployment preparation completed!")
    print("\n📋 Next Steps:")
    print("1. 📤 Push to GitHub:")
    print("   git push origin main")
    print("2. 🌐 Go to render.com and connect your repository")
    print("3. ⚙️  Configure environment variables in Render dashboard")
    print("4. 🚀 Render will auto-deploy your application")
    
    print("\n📚 Documentation:")
    print("- RENDER_DEPLOYMENT_GUIDE.md - Complete deployment guide")
    print("- README.md - Project documentation")
    print("- CODING_STANDARDS.md - Development guidelines")
    
    print("\n🔗 Important URLs after deployment:")
    print("- Frontend: https://your-app-name.onrender.com")
    print("- Backend: https://your-backend-name.onrender.com")
    print("- API Health: https://your-backend-name.onrender.com/health")

if __name__ == "__main__":
    main()
