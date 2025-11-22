"""
Load tests for deployment validation
Tests system under concurrent load
"""

import asyncio
import sys
import time
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


async def single_request(client, url, semaphore):
    """Make a single request with semaphore control"""
    async with semaphore:
        try:
            start_time = time.time()
            response = await client.get(url, timeout=30.0)
            end_time = time.time()

            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,
                "success": response.status_code == 200,
            }
        except Exception as e:
            return {"status_code": 0, "response_time": 0, "success": False, "error": str(e)}


async def run_load_tests():
    """Run load tests on critical endpoints"""

    base_url = "http://localhost"
    concurrent_requests = 10
    total_requests = 50

    print("Running Load Tests...")
    print(f"Concurrent Requests: {concurrent_requests}")
    print(f"Total Requests: {total_requests}")
    print("=" * 50)

    # Test endpoints
    endpoints = [
        f"{base_url}/api/v1/health",
        f"{base_url}/api/v1/cities/",
        f"{base_url}/api/v1/cities/Mumbai/rules",
        f"{base_url}/api/v1/cities/Pune/context",
    ]

    results = {}

    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            print(f"\nTesting: {endpoint}")

            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(concurrent_requests)

            # Create tasks
            tasks = []
            for _ in range(total_requests):
                task = single_request(client, endpoint, semaphore)
                tasks.append(task)

            # Run all requests
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            # Analyze results
            successful = sum(1 for r in responses if r["success"])
            failed = total_requests - successful
            avg_response_time = (
                sum(r["response_time"] for r in responses if r["success"]) / successful if successful > 0 else 0
            )
            max_response_time = max(r["response_time"] for r in responses if r["success"]) if successful > 0 else 0
            total_time = (end_time - start_time) * 1000
            requests_per_second = total_requests / (total_time / 1000) if total_time > 0 else 0

            results[endpoint] = {
                "total_requests": total_requests,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_requests) * 100,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "requests_per_second": requests_per_second,
                "total_time": total_time,
            }

            print(f"  Success Rate: {results[endpoint]['success_rate']:.1f}%")
            print(f"  Avg Response Time: {avg_response_time:.1f}ms")
            print(f"  Max Response Time: {max_response_time:.1f}ms")
            print(f"  Requests/Second: {requests_per_second:.1f}")

    # Overall summary
    print(f"\n{'='*50}")
    print("LOAD TEST SUMMARY")
    print(f"{'='*50}")

    overall_success = 0
    overall_total = 0

    for endpoint, result in results.items():
        overall_success += result["successful"]
        overall_total += result["total_requests"]

        endpoint_name = endpoint.split("/")[-1] or "health"
        print(f"{endpoint_name}: {result['success_rate']:.1f}% success, {result['avg_response_time']:.1f}ms avg")

    overall_success_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0

    print(f"\nOverall Success Rate: {overall_success_rate:.1f}%")

    # Determine if load test passed
    if overall_success_rate >= 95:  # 95% success rate threshold
        print("🎉 LOAD TESTS PASSED!")
        return True
    else:
        print("⚠️  LOAD TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_load_tests())
    sys.exit(0 if success else 1)
