#!/usr/bin/env python3

import os
import sys
import traceback

# Add current directory to path
sys.path.insert(0, ".")


def test_ppo_training():
    try:
        print("Testing PPO training...")

        # Test imports
        print("1. Testing imports...")
        import torch

        print(f"   PyTorch: {torch.__version__}")

        import stable_baselines3

        print(f"   Stable Baselines3: {stable_baselines3.__version__}")

        import gymnasium

        print(f"   Gymnasium: {gymnasium.__version__}")

        # Test reward model loading
        print("2. Testing reward model...")
        from app.rlhf.reward_model import SimpleRewardModel

        rm = SimpleRewardModel()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")

        if os.path.exists("models_ckpt/rm.pt"):
            rm.load_state_dict(torch.load("models_ckpt/rm.pt", map_location=device))
            print("   Reward model loaded successfully")
        else:
            print("   ERROR: Reward model not found")
            return

        # Test environment creation
        print("3. Testing environment...")
        from app.opt_rl.env_spec import SpecEditEnv

        base_spec = {"objects": [{"id": "floor_1", "type": "floor", "material": "wood"}], "scene": {}}
        env = SpecEditEnv(base_spec=base_spec, device=device)
        print("   Environment created successfully")

        # Test environment reset
        obs, info = env.reset()
        print(f"   Environment reset successful, obs shape: {obs.shape}")

        # Test PPO creation
        print("4. Testing PPO...")
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_util import make_vec_env

        def _make():
            return SpecEditEnv(base_spec=base_spec, device=device)

        vec_env = make_vec_env(_make, n_envs=1)
        print("   Vectorized environment created")

        model = PPO("MlpPolicy", vec_env, verbose=1, n_steps=64, batch_size=64, learning_rate=3e-4)
        print("   PPO model created successfully")

        # Test short training
        print("5. Testing training (10 steps)...")
        model.learn(total_timesteps=10)
        print("   Training completed successfully")

        # Test saving
        os.makedirs("models_ckpt/opt_ppo", exist_ok=True)
        out_path = "models_ckpt/opt_ppo/test_policy.zip"
        model.save(out_path)
        print(f"   Model saved to: {out_path}")

        print("SUCCESS: All tests passed!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_ppo_training()
