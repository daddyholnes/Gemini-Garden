#!/usr/bin/env python3
"""
Security utility script for Gemini Garden
Helps verify that credentials are properly secured
"""
import os
import stat
import sys
import json
import platform
from pathlib import Path

def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"

def check_service_account_file():
    """Check if service account file has secure permissions"""
    service_account_path = Path("camera-calibration-beta-51a46d9d1055.json")
    
    if not service_account_path.exists():
        print("❌ Service account file not found")
        return False
        
    try:
        # Check content format
        with open(service_account_path, 'r') as f:
            try:
                data = json.load(f)
                required_fields = ["type", "project_id", "private_key_id", "private_key", 
                                  "client_email", "client_id", "auth_uri", "token_uri"]
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Service account file missing field: {field}")
                        return False
                
                print("✅ Service account file format looks good")
                
                # Skip permission check on Windows
                if is_windows():
                    print("ℹ️ Windows detected - file permission checks skipped")
                    print("  Recommendation: Secure this file with Windows file permissions")
                    return True
                else:
                    # Check file permissions on Unix/Linux
                    file_stat = os.stat(service_account_path)
                    if file_stat.st_mode & stat.S_IROTH or file_stat.st_mode & stat.S_IWOTH:
                        print("❌ Service account file has insecure permissions (world-readable)")
                        print("   Fix with: chmod 600 camera-calibration-beta-51a46d9d1055.json")
                        return False
                    
                    print("✅ Service account file permissions look good")
                    return True
            except json.JSONDecodeError:
                print("❌ Service account file is not valid JSON")
                return False
    except Exception as e:
        print(f"❌ Error checking service account file: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    try:
        # Check required variables
        required_vars = ["DATABASE_URL", "OPENAI_API_KEY"]
        
        with open(env_path, 'r') as f:
            env_content = f.read()
            missing_vars = []
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"❌ .env file missing required variables: {', '.join(missing_vars)}")
                return False
            
            print("✅ .env file contains required variables")
            
            # Skip permission check on Windows
            if is_windows():
                print("ℹ️ Windows detected - file permission checks skipped")
                print("  Recommendation: Secure the .env file with Windows file permissions")
                return True
            else:
                # Check file permissions on Unix/Linux
                file_stat = os.stat(env_path)
                if file_stat.st_mode & stat.S_IROTH or file_stat.st_mode & stat.S_IWOTH:
                    print("❌ .env file has insecure permissions (world-readable)")
                    print("   Fix with: chmod 600 .env")
                    return False
                
                print("✅ .env file permissions look good")
                return True
            
    except Exception as e:
        print(f"❌ Error checking .env file: {e}")
        return False

def check_gitignore():
    """Check if .gitignore properly excludes sensitive files"""
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        print("❌ .gitignore file not found")
        return False
    
    try:
        with open(gitignore_path, 'r') as f:
            content = f.read()
            required_patterns = [
                ".env", 
                "*.json", 
                "*credentials*",
                "camera-calibration-beta-51a46d9d1055.json"
            ]
            
            missing_patterns = []
            for pattern in required_patterns:
                if pattern not in content:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                print(f"❌ .gitignore missing patterns: {', '.join(missing_patterns)}")
                return False
            
            print("✅ .gitignore properly excludes sensitive files")
            return True
    except Exception as e:
        print(f"❌ Error checking .gitignore: {e}")
        return False

def provide_windows_recommendations():
    """Provide Windows-specific recommendations"""
    print("\n--- Windows Security Recommendations ---")
    print("1. Secure service account and .env files with Windows file permissions:")
    print("   - Right-click on file > Properties > Security > Advanced")
    print("   - Remove inheritance > Convert inherited permissions to explicit permissions")
    print("   - Remove all users except yourself and necessary system accounts")
    
    print("\n2. For Docker Desktop on Windows:")
    print("   - Make sure WSL 2 is properly configured for Docker Desktop")
    print("   - Check resource allocation in Docker Desktop Settings")
    print("   - Ensure Docker Desktop has access to the drive with your project")

def provide_recommendations():
    """Provide security recommendations"""
    print("\n--- Security Recommendations ---")
    print("1. Never commit service account keys to repositories")
    print("2. Use Docker secrets or Kubernetes secrets for production deployments")
    print("3. Consider using workload identity federation instead of service account keys")
    print("4. Regularly rotate API keys and credentials")
    print("5. Apply the principle of least privilege for service accounts")
    print("6. Use environment variables instead of hard-coded values")
    print("7. Implement proper access controls and logging")
    print("8. Consider using a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.)")

if __name__ == "__main__":
    print("Running Gemini Garden security checks...\n")
    
    service_account_ok = check_service_account_file()
    env_ok = check_env_file()
    gitignore_ok = check_gitignore()
    
    print("\nSecurity check summary:")
    print(f"- Service account file: {'✅' if service_account_ok else '❌'}")
    print(f"- Environment variables: {'✅' if env_ok else '❌'}")
    print(f"- Gitignore configuration: {'✅' if gitignore_ok else '❌'}")
    
    if service_account_ok and env_ok and gitignore_ok:
        print("\n✅ All security checks passed!")
    else:
        print("\n❌ Some security checks failed. Please review the issues above.")
    
    provide_recommendations()
    
    if is_windows():
        provide_windows_recommendations()