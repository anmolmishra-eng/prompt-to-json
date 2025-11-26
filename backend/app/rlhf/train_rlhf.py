import json

import torch
from app.rlhf.reward_model import SimpleRewardModel, hash_tokenize
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from trl import AutoModelForCausalLMWithValueHead, PPOConfig, PPOTrainer
except ImportError:
    # TRL not available - use mock classes
    class AutoModelForCausalLMWithValueHead:
        @classmethod
        def from_pretrained(cls, model):
            return cls()

        def to(self, device):
            return self

        def generate(self, **kwargs):
            return torch.tensor([[1, 2, 3]])

        def save_pretrained(self, path):
            pass

    class PPOConfig:
        def __init__(self, **kwargs):
            self.batch_size = kwargs.get("batch_size", 2)
            self.mini_batch_size = kwargs.get("mini_batch_size", 2)
            self.num_ppo_epochs = kwargs.get("num_ppo_epochs", 4)
            self.learning_rate = kwargs.get("learning_rate", 1e-5)

    class PPOTrainer:
        def __init__(self, config, model, tokenizer):
            pass

        def step(self, input_ids, gen, rewards):
            pass


def _jsonify(txt: str):
    try:
        return json.loads(txt)
    except:
        return {"objects": [], "scene": {}}


def build_prompts(db, limit=200):
    rows = db.execute("SELECT prompt FROM specs ORDER BY created_at DESC LIMIT :n", {"n": limit}).fetchall()
    return [r[0] for r in rows] or ["Design a living room with marble floor and grey sofa"]


def rlhf_train(db, base_model_name="gpt2", steps=500, device="cpu"):
    tok = AutoTokenizer.from_pretrained(base_model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(base_model_name)
    policy = AutoModelForCausalLMWithValueHead.from_pretrained(base).to(device)

    rm = SimpleRewardModel()
    rm.load_state_dict(torch.load("models_ckpt/rm.pt", map_location=device))
    rm.to(device).eval()

    cfg = PPOConfig(batch_size=2, mini_batch_size=2, num_ppo_epochs=4, learning_rate=1e-5)
    ppo = PPOTrainer(cfg, policy, tok)

    prompts = build_prompts(db)
    for step in range(steps):
        batch_prompts = [prompts[step % len(prompts)] for _ in range(cfg.batch_size)]
        inputs = tok(batch_prompts, return_tensors="pt", padding=True).to(device)
        gen = policy.generate(**inputs, max_new_tokens=256)
        out = tok.batch_decode(gen, skip_special_tokens=True)

        responses = [t[len(p) :] if t.startswith(p) else t for t, p in zip(out, batch_prompts)]
        rewards = []
        for p, r in zip(batch_prompts, responses):
            spec = _jsonify(r)
            ids = hash_tokenize(p + " " + json.dumps(spec)).to(device).unsqueeze(0)
            with torch.no_grad():
                rew = rm(ids).item()
            rewards.append(rew)

        ppo.step(inputs["input_ids"], gen, torch.tensor(rewards).to(device))
        if step % 50 == 0:
            print(f"[RLHF] step {step} reward_mean={sum(rewards)/len(rewards):.3f}")

    save_dir = "models_ckpt/rlhf_policy"
    policy.save_pretrained(save_dir)
    return save_dir
