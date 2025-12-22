#!/usr/bin/env python3
"""
Test script for /api/v1/rl/train/rlhf endpoint
Tests RLHF training with reward model and PPO policy training
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
        if files_found["reward_model"]:
            files_found["rm_size"] = os.path.getsize(rm_path)

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

def test_rlhf_training():
    """Test RLHF training endpoint"""
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/rl/train/rlhf endpoint")
    print("=" * 60)

    # Check initial model files
    print("\nInitial model files check:")
    initial_files = check_model_files()
    print(f"Files found: {json.dumps(initial_files, indent=2)}")

    # Test 1: Standard RLHF training
    print("\n1. Testing standard RLHF training")
    payload = {
        "steps": 1000,
        "rm_epochs": 5
    }

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload, headers=headers)
    training_time = time.time() - start_time

    print(f"Status: {response.status_code}")
    print(f"Training time: {training_time:.2f} seconds")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    # Check if artifact was created
    if "artifact" in result:
        artifact_path = result["artifact"]
        print(f"Artifact path: {artifact_path}")

    # Test 2: Custom parameters
    print("\n2. Testing custom parameters")
    payload = {
        "steps": 500,
        "rm_epochs": 3,
        "learning_rate": 0.0001,
        "batch_size": 1024
    }

    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Minimal parameters
    print("\n3. Testing minimal parameters")
    payload = {
        "steps": 100
    }

    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Empty parameters (should use defaults)
    print("\n4. Testing empty parameters (should use defaults)")
    payload = {}

    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: No authentication (should fail)
    print("\n5. Testing without authentication (should fail)")
    payload = {"steps": 100}

    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: Large training job (should route to Yotta if available)
    print("\n6. Testing large training job")
    payload = {
        "steps": 5000,  # Large number to potentially trigger Yotta routing
        "rm_epochs": 10
    }

    response = requests.post(f"{BASE_URL}/rl/train/rlhf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Final model files check
    print("\n" + "="*60)
    print("FINAL MODEL FILES VERIFICATION")
    print("="*60)

    final_files = check_model_files()
    print(f"Final files: {json.dumps(final_files, indent=2)}")

    # Compare before and after
    if initial_files.get("all_files") != final_files.get("all_files"):
        print("\nNew files created during training:")
        initial_set = set(initial_files.get("all_files", []))
        final_set = set(final_files.get("all_files", []))
        new_files = final_set - initial_set
        for file in new_files:
            print(f"  + {file}")

    # Verify reward model exists
    if final_files.get("reward_model"):
        print(f"\nReward model: EXISTS ({final_files.get('rm_size', 0)} bytes)")
    else:
        print("\nReward model: NOT FOUND")

    # Verify PPO policy exists
    if final_files.get("ppo_policy"):
        print(f"PPO policy: EXISTS ({final_files.get('policy_size', 0)} bytes)")
    else:
        print("PPO policy: NOT FOUND")

    print("\nRLHF training endpoint tests completed!")

if __name__ == "__main__":
    test_rlhf_training()
