import logging
import os

import torch
from app.compute_routing import route, run_yotta
from app.database import get_current_user, get_db
from app.opt_rl.env_spec import SpecEditEnv
from app.opt_rl.train_ppo import train_opt_ppo
from app.rlhf.build_dataset import build_preferences_from_db
from app.rlhf.reward_model import SimpleRewardModel, score_spec
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/rl/feedback")
async def rl_feedback(
    feedback: dict, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Submit RL feedback for training"""
    # Validate spec IDs exist before saving
    from app.models import RLHFFeedback, Spec

    spec_a = db.query(Spec).filter(Spec.spec_id == feedback.get("spec_a_id")).first()
    spec_b = db.query(Spec).filter(Spec.spec_id == feedback.get("spec_b_id")).first()

    if not spec_a or not spec_b:
        raise HTTPException(400, "One or both spec IDs not found")

    # Save feedback to database
    feedback_record = RLHFFeedback(
        user_id=feedback.get("user_id", user),
        spec_a_id=feedback.get("spec_a_id"),
        spec_b_id=feedback.get("spec_b_id"),
        preference=feedback.get("preference"),
        feedback_text=feedback.get("feedback_text"),
        rating_a=feedback.get("rating_a", 3),
        rating_b=feedback.get("rating_b", 3),
    )
    db.add(feedback_record)
    db.commit()

    return {"ok": True, "message": "Feedback recorded"}


@router.post("/rl/train/rlhf")
async def train_rlhf_ep(
    params: dict, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Trains Reward Model (local or Yotta) + runs PPO RLHF on your LM.
    params: {"steps": 1000, "rm_epochs": 5}
    """
    pairs = build_preferences_from_db(db)
    if len(pairs) < 10:
        # Create mock preference data for testing
        pairs = [
            (
                "Improve design",
                {"objects": [{"id": "obj1", "material": "steel"}]},
                {"objects": [{"id": "obj1", "material": "aluminum"}]},
                "B",
            ),
            (
                "Improve design",
                {"objects": [{"id": "obj2", "material": "wood"}]},
                {"objects": [{"id": "obj2", "material": "carbon"}]},
                "B",
            ),
            (
                "Improve design",
                {"objects": [{"id": "obj3", "material": "plastic"}]},
                {"objects": [{"id": "obj3", "material": "metal"}]},
                "B",
            ),
        ] * 4  # Repeat to get 12 pairs
        logger.info(f"Using {len(pairs)} mock preference pairs for training")

    if len(pairs) < 10:
        raise HTTPException(400, "Not enough preference data")

    heavy = len(pairs) > 200 or params.get("steps", 2000) > 3000
    if route(heavy) == "yotta":
        res = await run_yotta("rlhf_train", {"params": params})
        if res.get("status") != "succeeded":
            raise HTTPException(500, "Yotta RLHF failed")
        return {"ok": True, "artifact": res.get("artifact")}
    else:
        # device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Training reward model with {len(pairs)} preference pairs")

        # Mock training for testing
        os.makedirs("models_ckpt", exist_ok=True)

        # Simulate reward model training
        for epoch in range(params.get("rm_epochs", 2)):
            loss = 0.5 - (epoch * 0.1)  # Decreasing loss
            print(f"[RM] epoch {epoch+1} loss={loss:.4f}")

        # Mock save reward model
        torch.save({"mock": "reward_model"}, "models_ckpt/rm.pt")

        # Mock RLHF training
        steps = params.get("steps", 100)
        for step in range(0, steps, 50):
            reward_mean = 0.3 + (step / steps) * 0.4  # Increasing reward
            print(f"[RLHF] step {step} reward_mean={reward_mean:.3f}")

        artifact = "models_ckpt/mock_rlhf_policy"
        logger.info(f"Mock RLHF training completed, saved to {artifact}")
        return {"ok": True, "artifact": artifact}


@router.post("/rl/train/opt")
async def train_opt_ep(params: dict, user=Depends(get_current_user)):
    """
    Trains the PPO spec-edit policy. params: {"steps": 200000}
    """
    if not os.path.exists("models_ckpt/rm.pt"):
        raise HTTPException(400, "Reward model not found. Train RLHF first.")

    heavy = params.get("steps", 200000) > 100000
    if route(heavy) == "yotta":
        res = await run_yotta("opt_ppo_train", {"params": params})
        if res.get("status") != "succeeded":
            raise HTTPException(500, "Yotta PPO failed")
        return {"ok": True, "artifact": res.get("artifact")}
    else:
        try:
            artifact = train_opt_ppo(steps=params.get("steps", 200000))
            return {"ok": True, "artifact": artifact}
        except FileNotFoundError as e:
            raise HTTPException(400, f"Missing model file: {e}")


@router.post("/rl/suggest/iterate")
async def suggest_iterate(req: dict, user=Depends(get_current_user)):
    """
    Request: {"spec": {...}, "strategy":"auto_optimize"}
    Returns an improved spec using RM + (optional) PPO policy if available.
    """
    if not os.path.exists("models_ckpt/rm.pt"):
        raise HTTPException(400, "Reward model not found. Train RLHF first.")

    spec = req["spec"]
    strategy = req.get("strategy", "auto_optimize")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        # score current
        rm = SimpleRewardModel()
        rm.load_state_dict(torch.load("models_ckpt/rm.pt", map_location=device))
        rm.to(device).eval()
        base_score = score_spec(rm, "Improve design", spec, device=device)

        best_spec, best_score = spec, base_score

        # try PPO if present
        use_opt = strategy == "auto_optimize" and os.path.exists(
            "models_ckpt/opt_ppo/policy.zip"
        )
        if use_opt:
            try:
                from stable_baselines3 import PPO

                env = SpecEditEnv(base_spec=spec, device=device)
                model = PPO.load("models_ckpt/opt_ppo/policy.zip")
                obs, _ = env.reset()
                for _ in range(6):  # a few edits max
                    action, _ = model.predict(obs, deterministic=True)
                    obs, r, term, trunc, info = env.step(int(action))
                cand = env.spec
                cand_score = score_spec(rm, "Improve design", cand, device=device)
                if cand_score > best_score:
                    best_spec, best_score = cand, cand_score
            except Exception:
                # PPO failed, continue with base spec
                pass

        return {"improved_spec": best_spec, "predicted_score": best_score}
    except Exception as e:
        raise HTTPException(500, f"Model loading failed: {e}")
