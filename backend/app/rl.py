"""
RL feedback endpoint stub
"""


async def rl_feedback(user_id: str, spec_id: str, rating: float, notes: str):
    """Stub for RL feedback processing"""
    return {"status": "processed", "training_triggered": False}
