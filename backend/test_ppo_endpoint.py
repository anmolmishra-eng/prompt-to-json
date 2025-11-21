#!/usr/bin/env python3

import json

import requests


def test_ppo_endpoint():
    """Test the PPO training endpoint"""

    # Login first
    login_data = {"username": "admin", "password": "admin"}
    login_response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test PPO training with small steps
    ppo_data = {
        "steps": 100,  # Small number for testing
        "learning_rate": 0.0003,
        "batch_size": 64,
        "n_epochs": 2,
        "gamma": 0.99,
        "gae_lambda": 0.95,
        "clip_range": 0.2,
    }

    print("Testing PPO training endpoint...")
    response = requests.post("http://localhost:8000/api/v1/rl/train/opt", json=ppo_data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    test_ppo_endpoint()
