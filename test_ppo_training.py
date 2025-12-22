#!/usr/bin/env python3
"""
Test script for /api/v1/rl/train/opt endpoint
Tests PPO spec-edit policy training
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get JWT token for authentication"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "user", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Auth failed: {response.text}")

def check_model_files():
    """Check if model files exist locally"""
    models_dir = "backend/models_ckpt"
    files_found = {}

    if os.path.exists(models_dir):
        # Check reward model
        rm_path = os.path.join(models_dir, "rm.pt")
        files_found["reward_model"] = os.path.exists(rm_path)

        # Check PPO policy
        ppo_dir = os.path.join(models_dir, "opt_ppo")
        if os.path.exists(ppo_dir):
            policy_path = os.path.join(ppo_dir, "policy.zip")
            files_found["ppo_policy"] = os.path.exists(policy_path)
            if files_found["ppo_policy"]:
                files_found["policy_size"] = os.path.getsize(policy_path)

        # List all files
        all_files = []
        for root, dirs, files in os.walk(models_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), models_dir)
                all_files.append(rel_path)
        files_found["all_files"] = all_files

    return files_found

def test_ppo_training():
    """Test PPO training endpoint"""
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/rl/train/opt endpoint")
    print("=" * 60)

    # Check initial model files
    print("\nInitial model files check:")
    initial_files = check_model_files()
    print(f"Reward model exists: {initial_files.get('reward_model', False)}")
    print(f"PPO policy exists: {initial_files.get('ppo_policy', False)}")

    # Test 1: Missing reward model (should fail)
    print("\n1. Testing missing reward model scenario")
    # Temporarily move reward model
    rm_path = "backend/models_ckpt/rm.pt"
    rm_backup = "backend/models_ckpt/rm.pt.backup"

    if os.path.exists(rm_path):
        os.rename(rm_path, rm_backup)

        payload = {"steps": 1000}
        response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        # Restore reward model
        os.rename(rm_backup, rm_path)

    # Test 2: No authentication (should fail)
    print("\n2. Testing without authentication (should fail)")
    payload = {"steps": 1000}
    response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Small training job (local execution - will fail due to mock reward model)
    print("\n3. Testing small PPO training job (local)")
    payload = {"steps": 1000}
    response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    # Test 4: Custom parameters (local execution)
    print("\n4. Testing custom parameters")
    payload = {
        "steps": 5000,
        "learning_rate": 0.0001,
        "batch_size": 1024,
        "n_epochs": 5
    }
    response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Large training job (should route to Yotta)
    print("\n5. Testing large PPO training job (Yotta routing)")
    payload = {"steps": 200000}  # Large number to trigger Yotta
    response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: Empty parameters (should use defaults)
    print("\n6. Testing empty parameters (defaults)")
    payload = {}
    response = requests.post(f"{BASE_URL}/rl/train/opt", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Final model files check
    print("\n" + "="*60)
    print("FINAL MODEL FILES VERIFICATION")
    print("="*60)

    final_files = check_model_files()
    print(f"Final files: {json.dumps(final_files, indent=2)}")

    # Check if PPO policy was updated
    if final_files.get("ppo_policy"):
        print(f"\nPPO Policy: EXISTS ({final_files.get('policy_size', 0)} bytes)")
    else:
        print("\nPPO Policy: NOT FOUND")

    print("\nPPO training endpoint tests completed!")

    # Summary of expected behavior
    print("\n" + "="*60)
    print("EXPECTED BEHAVIOR SUMMARY")
    print("="*60)
    print("1. Missing reward model: 400 error")
    print("2. No authentication: 403 error")
    print("3. Small jobs (< 100k steps): Local execution (fails due to mock reward model)")
    print("4. Large jobs (>= 100k steps): Yotta routing")
    print("5. Real training requires proper reward model from RLHF training")

if __name__ == "__main__":
    test_ppo_training()
