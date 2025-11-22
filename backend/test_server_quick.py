#!/usr/bin/env python3
"""
Quick Server Test - Test server startup without external dependencies
"""

import requests
import time
import subprocess
import sys
import signal
import os

def test_server_quick():
    """Test server startup with basic endpoints only"""
    print("Quick Server Test")
    print("=" * 20)
    
    server_process = None
    try:
        print("Starting server...")
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Waiting 3 seconds...")
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8001"
        
        # Test basic health endpoint
        try:
            response = requests.get(f"{base_url}/api/v1/health", timeout=3)
            print(f"[OK] Health endpoint: {response.status_code}")
            health_ok = response.status_code == 200
        except Exception as e:
            print(f"[FAIL] Health endpoint: {e}")
            health_ok = False
        
        # Test BHIV design endpoint structure (without external calls)
        try:
            # This should return 422 (validation error) but proves endpoint exists
            response = requests.post(f"{base_url}/bhiv/v1/design", json={}, timeout=3)
            print(f"[OK] BHIV design endpoint exists: {response.status_code}")
            bhiv_ok = response.status_code == 422  # Expected validation error
        except Exception as e:
            print(f"[FAIL] BHIV design endpoint: {e}")
            bhiv_ok = False
        
        return health_ok and bhiv_ok
        
    finally:
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server_process.kill()

def main():
    success = test_server_quick()
    
    if success:
        print("\n[SUCCESS] Server startup working!")
        print("- FastAPI app starts successfully")
        print("- Health endpoint responds")
        print("- BHIV endpoints are registered")
    else:
        print("\n[FAIL] Server startup issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)