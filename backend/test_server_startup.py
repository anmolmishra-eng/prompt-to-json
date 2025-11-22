#!/usr/bin/env python3
"""
Test server startup and endpoint availability
"""

import requests
import time
import subprocess
import sys
from threading import Thread
import signal
import os

def test_server_startup():
    """Test that the server starts and endpoints are accessible"""
    print("Testing Server Startup...")
    
    # Start server in background
    server_process = None
    try:
        print("Starting FastAPI server...")
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(5)
        
        # Test endpoints
        base_url = "http://localhost:8000"
        
        endpoints_to_test = [
            "/api/v1/health",
            "/bhiv/v1/health"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                print(f"   [OK] {endpoint} - Status: {response.status_code}")
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "success": False
                }
                print(f"   [FAIL] {endpoint} - Error: {e}")
        
        # Test BHIV design endpoint (POST)
        try:
            design_data = {
                "prompt": "Create a simple modern kitchen",
                "user_id": "test_user"
            }
            response = requests.post(f"{base_url}/bhiv/v1/design", json=design_data, timeout=10)
            results["/bhiv/v1/design"] = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 201]
            }
            print(f"   [OK] /bhiv/v1/design - Status: {response.status_code}")
        except Exception as e:
            results["/bhiv/v1/design"] = {
                "error": str(e),
                "success": False
            }
            print(f"   [FAIL] /bhiv/v1/design - Error: {e}")
        
        return results
        
    finally:
        # Clean up server process
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

def main():
    print("Server Startup Test")
    print("=" * 30)
    
    results = test_server_startup()
    
    print("\n" + "=" * 30)
    print("SERVER TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for r in results.values() if r.get("success", False))
    total = len(results)
    
    for endpoint, result in results.items():
        status = "[PASS]" if result.get("success", False) else "[FAIL]"
        print(f"{status} {endpoint}")
    
    print(f"\nResult: {passed}/{total} endpoints working")
    
    if passed == total:
        print("SUCCESS: Server startup and endpoints working!")
        return True
    else:
        print("WARNING: Some endpoints failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)