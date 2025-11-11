import hashlib
import json

import torch
import torch.nn as nn


def flatten_spec(spec_json: dict) -> str:
    return json.dumps(spec_json, sort_keys=True)


def hash_tokenize(text: str, vocab: int = 50000, max_len: int = 512):
    toks = text.split()
    ids = []
    for t in toks[:max_len]:
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        ids.append(h % vocab)
    if not ids:
        ids = [0]
    return torch.tensor(ids, dtype=torch.long)


class SimpleRewardModel(nn.Module):
    def __init__(self, vocab=50000, hidden=768):
        super().__init__()
        self.emb = nn.Embedding(vocab, 64)
        self.head = nn.Sequential(nn.Linear(64, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, ids):
        x = self.emb(ids).mean(dim=1)
        return self.head(x).squeeze(-1)


@torch.no_grad()
def score_spec(model: nn.Module, prompt: str, spec_json: dict, device="cpu") -> float:
    txt = prompt + " " + flatten_spec(spec_json)
    ids = hash_tokenize(txt).to(device).unsqueeze(0)
    model.eval()
    return float(model(ids).item())
