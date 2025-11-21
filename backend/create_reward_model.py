#!/usr/bin/env python3

import os

import torch
from app.rlhf.reward_model import SimpleRewardModel


def create_reward_model():
    """Create a proper reward model file"""
    print("Creating reward model...")

    # Create model
    model = SimpleRewardModel(vocab=50000, hidden=768)

    # Initialize with random weights (normally this would be trained)
    torch.nn.init.normal_(model.emb.weight, mean=0, std=0.1)
    torch.nn.init.normal_(model.head[0].weight, mean=0, std=0.1)
    torch.nn.init.zeros_(model.head[0].bias)
    torch.nn.init.normal_(model.head[2].weight, mean=0, std=0.1)
    torch.nn.init.zeros_(model.head[2].bias)

    # Save model
    os.makedirs("models_ckpt", exist_ok=True)
    torch.save(model.state_dict(), "models_ckpt/rm.pt")
    print("Reward model saved to models_ckpt/rm.pt")

    # Test loading
    test_model = SimpleRewardModel()
    test_model.load_state_dict(torch.load("models_ckpt/rm.pt"))
    print("Reward model loaded successfully")


if __name__ == "__main__":
    create_reward_model()
