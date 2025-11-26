"""
Test system health with all components showing as healthy (using mocks)
"""
import asyncio
from datetime import datetime, timezone

async def mock_system_health_check():
    """Mock system health check that shows all components as healthy"""

    # Mock all components as healthy
    components = [
        {
            "component": "database",
            "status": "healthy",
            "latency_ms": 45.0,
            "mock": True
        },
        {
            "component": "redis",
            "status": "healthy",
            "latency_ms": 25.0,
            "mock": True
        },
        {
            "component": "system_resources",
            "status": "healthy",
            "cpu_percent": 15.0,
            "memory_percent": 65.0,
            "disk_percent": 45.0
        },
        {
            "component": "api",
            "status": "healthy",
            "latency_ms": 120.0,
            "mock": True
        },
        {
            "component": "sohum_mcp",
            "status": "healthy",
            "latency_ms": 75.0,
            "mock": True
        },
        {
            "component": "ranjeet_rl",
            "status": "healthy",
            "latency_ms": 85.0,
            "mock": True
        }
    ]

    # Calculate summary
    healthy = [c for c in components if c["status"] == "healthy"]
    failed = [c for c in components if c["status"] == "unhealthy"]
    degraded = [c for c in components if c["status"] == "degraded"]

    # Calculate average latency
    latencies = [c.get("latency_ms", 0) for c in components if "latency_ms" in c]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    health_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": "healthy",
        "components": components,
        "summary": {
            "healthy": len(healthy),
            "degraded": len(degraded),
            "failed": len(failed),
            "total": len(components)
        },
        "failed_components": [],
        "degraded_components": [],
        "average_latency_ms": round(avg_latency, 2)
    }

    return health_report

if __name__ == "__main__":
    print("Testing All-Healthy System Health Check...")

    result = asyncio.run(mock_system_health_check())

    print(f"Overall Status: {result['overall_status']}")
    print(f"Summary: {result['summary']}")
    print(f"Average Latency: {result['average_latency_ms']}ms")

    print("\nComponent Details:")
    for comp in result['components']:
        status = comp['status']
        name = comp['component']
        latency = comp.get('latency_ms', 'N/A')
        mock = ' (mock)' if comp.get('mock') else ''
        print(f"  {name}: {status} - {latency}ms{mock}")

    print(f"\nResult: ALL {result['summary']['total']} COMPONENTS HEALTHY!")
    print("This shows what the workflow would look like with all services running.")
