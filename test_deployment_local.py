#!/usr/bin/env python3
"""
Local Deployment Testing Script
Test your deployment configuration locally before pushing to Render
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def main():
    """Main testing function"""
    print("🚀 Smart Rental Tracker - Local Deployment Testing")
    print("=" * 60)
    
    # Check deployment files
    print("\n📁 Checking deployment files...")
    files_to_check = [
        ("render.yaml", "Render configuration"),
        ("backend/config.env.production", "Backend production config"),
        ("backend/requirements.render.txt", "Backend production requirements"),
        ("backend/start_production.py", "Backend startup script"),
        ("backend/init_production_db.py", "Database initialization script"),
        ("frontend/build_production.sh", "Frontend build script"),
        ("RENDER_DEPLOYMENT_GUIDE.md", "Deployment guide"),
        ("DEPLOYMENT_CHECKLIST.md", "Deployment checklist")
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some deployment files are missing. Please create them first.")
        return False
    
    print("\n✅ All deployment files are present!")
    
    # Test backend requirements
    print("\n🐍 Testing backend requirements...")
    if not run_command("cd backend && pip check -r requirements.render.txt", "Checking backend requirements"):
        print("⚠️ Backend requirements have conflicts. This may cause deployment issues.")
    
    # Test frontend build
    print("\n⚛️ Testing frontend build...")
    if not run_command("cd frontend && npm install", "Installing frontend dependencies"):
        print("❌ Frontend dependencies failed to install")
        return False
    
    if not run_command("cd frontend && npm run build", "Building frontend"):
        print("❌ Frontend build failed")
        return False
    
    # Test backend startup script
    print("\n🐍 Testing backend startup script...")
    if not run_command("cd backend && python -m py_compile start_production.py", "Compiling backend startup script"):
        print("❌ Backend startup script has syntax errors")
        return False
    
    if not run_command("cd backend && python -m py_compile init_production_db.py", "Compiling database init script"):
        print("❌ Database init script has syntax errors")
        return False
    
    # Test environment configuration
    print("\n⚙️ Testing environment configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv('backend/config.env.production')
        print("✅ Production environment config loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load production environment: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Local deployment testing completed successfully!")
    print("\n📋 Next steps:")
    print("1. Commit all changes to GitHub")
    print("2. Push to your repository")
    print("3. Deploy on Render using the Blueprint")
    print("4. Follow the deployment checklist")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
