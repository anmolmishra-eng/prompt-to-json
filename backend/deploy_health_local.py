#!/usr/bin/env python3
"""
Local deployment script for system health monitoring
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from workflows.system_health_flow import system_health_flow


async def run_health_monitor():
    """Run the health monitor locally"""
    print("[HEALTH] Starting System Health Monitor...")

    # Get environment variables
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/designapi")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    api_url = "http://localhost:8000"
    sohum_url = os.getenv("SOHUM_URL", "http://localhost:8001")
    ranjeet_url = os.getenv("RANJEET_RL_URL", "http://localhost:8002")

    print(f"[CONFIG] Monitoring configuration:")
    print(f"   Database: {db_url[:50]}...")
    print(f"   Redis: {redis_url}")
    print(f"   API: {api_url}")
    print(f"   Sohum MCP: {sohum_url}")
    print(f"   Ranjeet RL: {ranjeet_url}")

    try:
        # Run the health check
        result = await system_health_flow(
            db_url=db_url, redis_url=redis_url, api_url=api_url, sohum_url=sohum_url, ranjeet_url=ranjeet_url
        )

        print(f"\n[SUCCESS] Health Check Complete!")
        print(f"   Overall Status: {result['overall_status']}")
        print(f"   Components: {result['summary']['healthy']}/{result['summary']['total']} healthy")

        if result["failed_components"]:
            print(f"   [FAILED] Failed: {', '.join(result['failed_components'])}")

        if result["degraded_components"]:
            print(f"   [WARNING] Degraded: {', '.join(result['degraded_components'])}")

        print(f"   Average Latency: {result['average_latency_ms']}ms")

        return result

    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return None


def run_continuous_monitoring():
    """Run continuous monitoring every 5 minutes"""
    import time

    print("[MONITOR] Starting continuous monitoring (every 5 minutes)")
    print("   Press Ctrl+C to stop")

    try:
        while True:
            print(f"\n{'='*60}")
            print(f"[CHECK] Health Check at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")

            # Run health check
            result = asyncio.run(run_health_monitor())

            if result and result["overall_status"] != "healthy":
                print(f"[WARNING] System not fully healthy - check logs above")

            # Wait 5 minutes
            print(f"\n[WAIT] Waiting 5 minutes until next check...")
            time.sleep(300)  # 5 minutes

    except KeyboardInterrupt:
        print(f"\n[STOP] Monitoring stopped by user")
    except Exception as e:
        print(f"[ERROR] Monitoring error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument("--once", action="store_true", help="Run once instead of continuously")
    parser.add_argument("--continuous", action="store_true", help="Run continuously every 5 minutes")

    args = parser.parse_args()

    if args.once:
        # Run once
        result = asyncio.run(run_health_monitor())
        sys.exit(0 if result and result["overall_status"] == "healthy" else 1)
    elif args.continuous:
        # Run continuously
        run_continuous_monitoring()
    else:
        # Default: run once
        print("Usage:")
        print("  python deploy_health_local.py --once       # Run health check once")
        print("  python deploy_health_local.py --continuous # Run continuously every 5 minutes")
        print()
        print("Running single health check...")
        result = asyncio.run(run_health_monitor())
        sys.exit(0 if result and result["overall_status"] == "healthy" else 1)
