import gymnasium as gym
import numpy as np, json, torch
from app.rlhf.reward_model import SimpleRewardModel, hash_tokenize

class SpecEditEnv(gym.Env):
    metadata = {"render_modes":[]}

    def __init__(self, base_spec, rm_ckpt="models_ckpt/rm.pt", device="cpu"):
        super().__init__()
        self.device = device
        self.rm = SimpleRewardModel()
        self.rm.load_state_dict(torch.load(rm_ckpt, map_location=device))
        self.rm.eval()
        self.base = base_spec
        self.spec = None

        self.actions = [
            ("floor_1","material","marble_white"),
            ("sofa_1","material","leather_brown"),
            ("cushion_1","material","fabric_orange"),
        ]
        self.action_space = gym.spaces.Discrete(len(self.actions))
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(512,), dtype=np.float32)

    def _embed(self, spec_json):
        txt = json.dumps(spec_json, sort_keys=True)
        ids = hash_tokenize(txt, max_len=512).cpu().numpy()
        vec = np.zeros(512, dtype=np.float32)
        L = min(len(ids), 512); vec[:L] = (np.array(ids[:L]) % 997) / 997.0
        return vec

    @torch.no_grad()
    def _rm_score(self, spec_json):
        ids = hash_tokenize(json.dumps(spec_json)).to(self.device).unsqueeze(0)
        return float(self.rm(ids).item())

    def reset(self, seed=None, options=None):
        self.spec = json.loads(json.dumps(self.base))
        return self._embed(self.spec), {}

    def step(self, action_idx):
        obj_id, field, value = self.actions[int(action_idx)]
        for obj in self.spec.get("objects", []):
            if obj.get("id") == obj_id:
                obj[field] = value
                break
        r = self._rm_score(self.spec)
        terminated, truncated = False, False
        return self._embed(self.spec), r, terminated, truncated, {}