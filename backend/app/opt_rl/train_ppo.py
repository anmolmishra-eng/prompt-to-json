import json
import os

import torch
from app.opt_rl.env_spec import SpecEditEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env


def load_base_spec(path="seed_spec.json"):
    if os.path.exists(path):
        return json.load(open(path))
    return {
        "objects": [{"id": "floor_1", "type": "floor", "material": "wood"}],
        "scene": {},
    }


def train_opt_ppo(steps=200_000, n_envs=4):
    base = load_base_spec()

    def _make():
        return SpecEditEnv(base_spec=base, device="cuda" if torch.cuda.is_available() else "cpu")

    env = make_vec_env(_make, n_envs=n_envs)
    model = PPO("MlpPolicy", env, verbose=1, n_steps=512, batch_size=2048, learning_rate=3e-4)
    model.learn(total_timesteps=steps)
    os.makedirs("models_ckpt/opt_ppo", exist_ok=True)
    out = "models_ckpt/opt_ppo/policy.zip"
    model.save(out)
    return out
