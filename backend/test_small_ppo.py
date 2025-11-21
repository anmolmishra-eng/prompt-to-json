#!/usr/bin/env python3

import json

import requests


def test_small_ppo():
    # Login
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login", json={"username": "admin", "password": "admin"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Small PPO test
    ppo_data = {"steps": 100}

    response = requests.post("http://localhost:8000/api/v1/rl/train/opt", json=ppo_data, headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    test_small_ppo()
