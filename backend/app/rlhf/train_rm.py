import torch, torch.optim as optim
from app.rlhf.reward_model import SimpleRewardModel, hash_tokenize, flatten_spec

def train_reward_model(pairs, device="cpu", epochs=5, lr=1e-4, vocab=50000, margin=0.5):
    model = SimpleRewardModel(vocab=vocab).to(device)
    opt = optim.AdamW(model.parameters(), lr=lr)
    for ep in range(epochs):
        total = 0.0
        for prompt, A, B, pref in pairs:
            model.train(); opt.zero_grad()
            def s(spec):
                txt = prompt + " " + flatten_spec(spec)
                ids = hash_tokenize(txt).to(device).unsqueeze(0)
                return model(ids).squeeze()
            rA, rB = s(A), s(B)
            if pref == "A":
                loss = torch.relu(margin - (rA - rB))
            else:
                loss = torch.relu(margin - (rB - rA))
            loss.backward(); opt.step()
            total += float(loss.item())
        print(f"[RM] epoch {ep+1} loss={total/max(1,len(pairs)):.4f}")
    return model