#!/usr/bin/env python3
"""
SIDMS Vercel Deployment Helper Script
This script helps prepare the project for Vercel deployment
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
    
    # Check Vercel CLI
    success, _, _ = run_command("vercel --version")
    if not success:
        print("⚠️  Vercel CLI not found. Installing...")
        success, _, error = run_command("npm install -g vercel")
        if not success:
            print(f"❌ Failed to install Vercel CLI: {error}")
            return False
        print("✅ Vercel CLI installed")
    else:
        print("✅ Vercel CLI found")
    
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
    
    # Check if api directory exists
    api_path = backend_path / "api"
    api_path.mkdir(exist_ok=True)
    
    # Copy requirements file for Vercel
    req_file = backend_path / "requirements-vercel.txt"
    if req_file.exists():
        print("   Vercel requirements file found")
    else:
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
            print("❌ Deployment cancelled for security reasons")
            return False
    else:
        print("✅ Admin credentials appear to be customized")
    
    return True

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Deploying to Vercel...")
    
    # Check if already logged in
    success, _, _ = run_command("vercel whoami")
    if not success:
        print("   Please login to Vercel:")
        success, _, error = run_command("vercel login")
        if not success:
            print(f"❌ Failed to login to Vercel: {error}")
            return False
    
    # Deploy
    print("   Starting deployment...")
    success, output, error = run_command("vercel --prod")
    if not success:
        print(f"❌ Deployment failed: {error}")
        return False
    
    print("✅ Deployment completed!")
    print("\n📋 Deployment Output:")
    print(output)
    
    return True

def main():
    """Main deployment function"""
    print("🚀 SIDMS Vercel Deployment Helper")
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
    
    # Deploy
    if not deploy_to_vercel():
        print("\n❌ Deployment failed.")
        return
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📝 Next Steps:")
    print("1. Configure environment variables in Vercel dashboard")
    print("2. Test your application at the provided URL")
    print("3. Set up MongoDB Atlas IP whitelist if needed")
    print("4. Monitor Vercel logs for any issues")
    
    print("\n📚 Documentation:")
    print("- DEPLOYMENT_GUIDE.md - Complete deployment guide")
    print("- README.md - Project documentation")
    print("- CODING_STANDARDS.md - Development guidelines")

if __name__ == "__main__":
    main()
