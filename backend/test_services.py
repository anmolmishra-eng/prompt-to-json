"""
Test BHIV Services
Check if all services are running and responding
"""

import asyncio
import sys

import httpx


async def test_services():
    """Test all BHIV services"""
    print("=== BHIV Services Test ===")

    services = [
        ("Main Backend", "http://localhost:8000/api/v1/health"),
        ("BHIV Assistant", "http://localhost:8003/health"),
        ("Prefect Server", "http://localhost:4200/api/health"),
        ("Sohum MCP Service", "https://ai-rule-api-w7z5.onrender.com/health"),
    ]

    results = {}

    async with httpx.AsyncClient(timeout=15.0) as client:
        for name, url in services:
            print(f"\nTesting {name}...")
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"[PASS] {name}: RUNNING")
                    try:
                        data = response.json()
                        if "status" in data:
                            print(f"  Status: {data['status']}")
                    except:
                        pass
                    results[name] = True
                else:
                    print(f"[FAIL] {name}: HTTP {response.status_code}")
                    results[name] = False
            except httpx.ConnectError:
                print(f"[FAIL] {name}: NOT RUNNING (connection refused)")
                results[name] = False
            except httpx.TimeoutException:
                print(f"[FAIL] {name}: TIMEOUT")
                results[name] = False
            except Exception as e:
                print(f"[FAIL] {name}: ERROR - {str(e)[:50]}")
                results[name] = False

    print("\n=== Service Results ===")
    running = 0
    for service, status in results.items():
        status_text = "RUNNING" if status else "NOT RUNNING"
        print(f"{service}: {status_text}")
        if status:
            running += 1

    print(f"\nOverall: {running}/{len(services)} services running")

    if running == 0:
        print("\nNo services are running. Start them with:")
        print("1. python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. cd app/bhiv_assistant && python start_bhiv.py")
        print("3. prefect server start")
    elif running < len(services):
        print(f"\nSome services are not running. Check the failed services above.")
    else:
        print("\nAll services are running! System is ready.")

    return running == len(services)


async def test_api_endpoints():
    """Test key API endpoints"""
    print("\n=== API Endpoints Test ===")

    endpoints = [
        ("Health Check", "GET", "http://localhost:8000/api/v1/health", None),
        ("Cities List", "GET", "http://localhost:8000/api/v1/cities/", None),
        ("Mumbai Rules", "GET", "http://localhost:8000/api/v1/cities/Mumbai/rules", None),
    ]

    results = {}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, method, url, payload in endpoints:
            print(f"\nTesting {name}...")
            try:
                if method == "GET":
                    response = await client.get(url)
                else:
                    response = await client.post(url, json=payload)

                if response.status_code in [200, 201]:
                    print(f"[PASS] {name}: {response.status_code}")
                    results[name] = True
                else:
                    print(f"[FAIL] {name}: HTTP {response.status_code}")
                    results[name] = False

            except Exception as e:
                print(f"[FAIL] {name}: {str(e)[:50]}")
                results[name] = False

    print("\n=== API Results ===")
    working = 0
    for endpoint, status in results.items():
        status_text = "WORKING" if status else "FAILED"
        print(f"{endpoint}: {status_text}")
        if status:
            working += 1

    print(f"\nAPI Endpoints: {working}/{len(endpoints)} working")
    return working == len(endpoints)


async def main():
    """Run all service tests"""
    print("Testing BHIV System Services...")

    # Test services
    services_ok = await test_services()

    # Test API endpoints if main backend is running
    api_ok = True
    if services_ok or any("Main Backend" in str(results) for results in []):
        api_ok = await test_api_endpoints()

    print("\n=== Final Results ===")
    if services_ok and api_ok:
        print("SUCCESS: All services and APIs are working!")
        return True
    else:
        print("PARTIAL: Some services or APIs need attention.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
