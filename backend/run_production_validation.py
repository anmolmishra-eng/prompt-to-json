"""
Production Validation - Multi-City Full Flow
Tests complete pipeline: prompt → JSON → MCP → RL → geometry → feedback → training
"""
import json
import os
import time
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "production_validation_results"

# Test cases per city
TEST_CASES = {
    "Mumbai": [
        "Design a 3BHK apartment with modern kitchen",
        "Create a commercial office space with parking",
        "Design a residential building with 4 floors",
        "Build a luxury penthouse with terrace",
        "Design a compact studio apartment",
    ],
    "Pune": [
        "Design a residential villa with garden and parking for 2 cars",
        "Create a tech office with open workspace",
        "Design a row house with 3 bedrooms",
        "Build a duplex with rooftop access",
        "Design a bungalow with swimming pool",
    ],
    "Ahmedabad": [
        "Design a traditional house with courtyard",
        "Create a commercial complex with shops",
        "Design a residential tower with amenities",
        "Build a warehouse with loading dock",
        "Design a farmhouse with guest rooms",
    ],
    "Nashik": [
        "Design a vineyard resort with cottages",
        "Create a residential colony layout",
        "Design a temple complex with halls",
        "Build a school building with playground",
        "Design a hospital with emergency wing",
    ],
}


def get_token():
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": "admin", "password": "bhiv2024"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return r.json()["access_token"]


def run_full_flow(city, prompt, flow_id, token):
    """Run complete flow and capture all steps"""
    log = []
    result = {"flow_id": flow_id, "city": city, "prompt": prompt, "timestamp": datetime.now().isoformat(), "steps": {}}

    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Generate
    log.append(f"[{flow_id}] Step 1: Generate design")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": prompt, "city": city, "user_id": "admin"},
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            result["steps"]["generate"] = {"status": "success", "spec_id": data.get("spec_id"), "response": data}
            spec_id = data.get("spec_id")
            log.append(f"[{flow_id}] Generate: SUCCESS - {spec_id}")
        else:
            result["steps"]["generate"] = {"status": "error", "code": r.status_code, "error": r.text[:500]}
            log.append(f"[{flow_id}] Generate: FAILED - {r.status_code}")
            return result, log
    except Exception as e:
        result["steps"]["generate"] = {"status": "error", "error": str(e)}
        log.append(f"[{flow_id}] Generate: ERROR - {e}")
        return result, log

    # Step 2: MCP Compliance (if available)
    log.append(f"[{flow_id}] Step 2: MCP compliance check")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/compliance/run_case",
            json={
                "project_id": f"proj_{flow_id}",
                "case_id": f"{city.lower()}_case",
                "city": city,
                "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
            },
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            result["steps"]["mcp"] = {"status": "success", "response": r.json()}
            log.append(f"[{flow_id}] MCP: SUCCESS")
        else:
            result["steps"]["mcp"] = {"status": "error", "error": r.text[:200]}
            log.append(f"[{flow_id}] MCP: SKIPPED")
    except Exception as e:
        result["steps"]["mcp"] = {"status": "error", "error": str(e)[:200]}
        log.append(f"[{flow_id}] MCP: ERROR")

    # Step 3: RL Optimization
    log.append(f"[{flow_id}] Step 3: RL optimization")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/rl/suggest_iterate",
            json={"spec_id": spec_id, "city": city},
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            result["steps"]["rl_optimize"] = {"status": "success", "response": r.json()}
            log.append(f"[{flow_id}] RL: SUCCESS")
        else:
            result["steps"]["rl_optimize"] = {"status": "error", "error": r.text[:200]}
            log.append(f"[{flow_id}] RL: SKIPPED")
    except Exception as e:
        result["steps"]["rl_optimize"] = {"status": "error", "error": str(e)[:200]}
        log.append(f"[{flow_id}] RL: ERROR")

    # Step 4: Geometry Generation
    log.append(f"[{flow_id}] Step 4: Generate geometry")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/geometry/generate",
            json={"request_id": flow_id, "spec_json": result["steps"]["generate"]["response"].get("spec_json", {})},
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            result["steps"]["geometry"] = {"status": "success", "response": r.json()}
            log.append(f"[{flow_id}] Geometry: SUCCESS")
        else:
            result["steps"]["geometry"] = {"status": "error", "error": r.text[:200]}
            log.append(f"[{flow_id}] Geometry: FAILED")
    except Exception as e:
        result["steps"]["geometry"] = {"status": "error", "error": str(e)[:200]}
        log.append(f"[{flow_id}] Geometry: ERROR")

    # Step 5: Feedback
    log.append(f"[{flow_id}] Step 5: Submit feedback")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/rl/feedback",
            json={
                "spec_id": spec_id,
                "user_rating": 4.5,
                "city": city,
                "design_spec": result["steps"]["generate"]["response"].get("spec_json", {}),
            },
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            result["steps"]["feedback"] = {"status": "success", "response": r.json()}
            log.append(f"[{flow_id}] Feedback: SUCCESS")
        else:
            result["steps"]["feedback"] = {"status": "error", "error": r.text[:200]}
            log.append(f"[{flow_id}] Feedback: FAILED")
    except Exception as e:
        result["steps"]["feedback"] = {"status": "error", "error": str(e)[:200]}
        log.append(f"[{flow_id}] Feedback: ERROR")

    # Step 6: Training
    log.append(f"[{flow_id}] Step 6: Trigger training")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/rl/train/rlhf", json={"batch_size": 1, "epochs": 1}, headers=headers, timeout=30
        )
        if r.status_code == 200:
            result["steps"]["training"] = {"status": "success", "response": r.json()}
            log.append(f"[{flow_id}] Training: SUCCESS")
        else:
            result["steps"]["training"] = {"status": "error", "error": r.text[:200]}
            log.append(f"[{flow_id}] Training: FAILED")
    except Exception as e:
        result["steps"]["training"] = {"status": "error", "error": str(e)[:200]}
        log.append(f"[{flow_id}] Training: ERROR")

    return result, log


def save_results(flow_id, result, log):
    """Save response JSON and log file"""
    # Save response
    response_file = f"{OUTPUT_DIR}/responses/{flow_id}.json"
    with open(response_file, "w") as f:
        json.dump(result, f, indent=2)

    # Save log
    log_file = f"{OUTPUT_DIR}/logs/{flow_id}.log"
    with open(log_file, "w") as f:
        f.write("\n".join(log))

    return response_file, log_file


def main():
    print("=" * 70)
    print("PRODUCTION VALIDATION - MULTI-CITY FULL FLOW")
    print("=" * 70)

    # Setup directories
    os.makedirs(f"{OUTPUT_DIR}/responses", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/logs", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/glbs", exist_ok=True)

    # Get token
    print("\nAuthenticating...")
    token = get_token()
    print("OK - Authenticated")

    # Run tests
    total_tests = sum(len(cases) for cases in TEST_CASES.values())
    current = 0
    results_summary = []

    for city, prompts in TEST_CASES.items():
        print(f"\n{'='*70}")
        print(f"TESTING: {city.upper()}")
        print(f"{'='*70}")

        for i, prompt in enumerate(prompts, 1):
            current += 1
            flow_id = f"{city.lower()}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            print(f"\n[{current}/{total_tests}] {flow_id}")
            print(f"Prompt: {prompt[:50]}...")

            # Run flow
            result, log = run_full_flow(city, prompt, flow_id, token)

            # Save results
            response_file, log_file = save_results(flow_id, result, log)

            # Summary
            steps_status = {k: v.get("status") for k, v in result["steps"].items()}
            success_count = sum(1 for s in steps_status.values() if s == "success")

            results_summary.append(
                {
                    "flow_id": flow_id,
                    "city": city,
                    "steps": steps_status,
                    "success_rate": f"{success_count}/{len(steps_status)}",
                }
            )

            print(f"Steps: {steps_status}")
            print(f"Success: {success_count}/{len(steps_status)}")
            print(f"Saved: {response_file}")

            time.sleep(1)  # Rate limiting

    # Final summary
    print(f"\n{'='*70}")
    print("VALIDATION COMPLETE")
    print(f"{'='*70}")

    summary_file = f"{OUTPUT_DIR}/validation_summary.json"
    with open(summary_file, "w") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "total_tests": total_tests, "results": results_summary},
            f,
            indent=2,
        )

    print(f"\nTotal tests: {total_tests}")
    print(f"Summary: {summary_file}")

    # Print city breakdown
    for city in TEST_CASES.keys():
        city_results = [r for r in results_summary if r["city"] == city]
        print(f"\n{city}: {len(city_results)} tests")
        for r in city_results:
            print(f"  {r['flow_id']}: {r['success_rate']}")


if __name__ == "__main__":
    main()
