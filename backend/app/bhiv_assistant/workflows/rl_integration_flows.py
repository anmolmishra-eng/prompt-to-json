import json
import os
from typing import Any, Dict

from prefect import flow, get_run_logger, task


@task
def load_rl_model(model_path: str = "models_ckpt/opt_ppo/policy.zip"):
    """Load existing RL model"""
    logger = get_run_logger()

    try:
        from stable_baselines3 import PPO

        if os.path.exists(model_path):
            model = PPO.load(model_path)
            logger.info(f"Loaded RL model from {model_path}")
            return model
        else:
            logger.warning(f"Model not found at {model_path}, using mock model")
            return None
    except Exception as e:
        logger.error(f"Failed to load RL model: {e}")
        return None


@task
def run_rl_agent(state_input: Dict[str, Any], model_path: str = "models_ckpt/opt_ppo/policy.zip"):
    """Use existing RL code in the repo"""
    logger = get_run_logger()

    try:
        # Import existing RL components
        from app.opt_rl.env_spec import SpecEditEnv
        from app.opt_rl.train_ppo import load_base_spec
        from stable_baselines3 import PPO

        # Load base spec
        base_spec = load_base_spec()

        # Create environment
        env = SpecEditEnv(base_spec=base_spec, device="cpu")

        # Load trained model if available
        if os.path.exists(model_path):
            model = PPO.load(model_path)
            logger.info("Using trained PPO model")

            # Get observation from environment
            obs, _ = env.reset()

            # Predict action
            action, _ = model.predict(obs, deterministic=True)

            # Take action in environment
            obs, reward, terminated, truncated, info = env.step(action)

            result = {"action": int(action), "reward": float(reward), "spec": env.spec, "terminated": terminated}
        else:
            logger.warning("No trained model found, using mock result")
            result = {"action": 0, "reward": 0.75, "spec": base_spec, "terminated": False}

        logger.info(f"RL agent result: reward={result['reward']}")
        return result

    except Exception as e:
        logger.error(f"RL agent failed: {e}")
        return {"error": str(e), "reward": 0.0}


@task
def train_rl_model(training_steps: int = 10000, **kwargs):
    """Train RL model using existing training code"""
    logger = get_run_logger()

    try:
        from app.opt_rl.train_ppo import train_opt_ppo

        logger.info(f"Starting RL training for {training_steps} steps")

        # Use existing training function
        model_path = train_opt_ppo(steps=training_steps, n_envs=2, **kwargs)  # Reduced for faster training

        logger.info(f"Training completed, model saved to: {model_path}")
        return {"model_path": model_path, "training_steps": training_steps}

    except Exception as e:
        logger.error(f"RL training failed: {e}")
        return {"error": str(e)}


@task
def evaluate_planning(spec_input: Dict[str, Any]):
    """Evaluate planning using RL model"""
    logger = get_run_logger()

    try:
        # Use existing RL environment for evaluation
        from app.opt_rl.env_spec import SpecEditEnv

        # Create environment with input spec
        env = SpecEditEnv(base_spec=spec_input, device="cpu")

        # Reset environment
        obs, _ = env.reset()

        # Calculate reward for current spec
        reward = env._rm_score(spec_input)

        result = {
            "planning_score": float(reward),
            "spec_evaluation": "completed",
            "recommendations": [
                "Consider material optimization",
                "Evaluate space utilization",
                "Check aesthetic coherence",
            ],
        }

        logger.info(f"Planning evaluation: score={reward}")
        return result

    except Exception as e:
        logger.error(f"Planning evaluation failed: {e}")
        return {"error": str(e), "planning_score": 0.0}


@flow
def rl_optimization_flow(prompt: str, city: str = "Mumbai"):
    """Complete RL optimization flow using existing models"""
    logger = get_run_logger()
    logger.info(f"Starting RL optimization for {city}: {prompt}")

    # Create state input from prompt
    state_input = {
        "prompt": prompt,
        "city": city,
        "objects": [{"id": "base_object", "type": "room", "material": "default"}],
        "scene": {"city": city},
    }

    # Run RL agent
    rl_result = run_rl_agent(state_input)

    # Evaluate planning
    planning_result = evaluate_planning(state_input)

    # Combine results
    final_result = {
        "prompt": prompt,
        "city": city,
        "rl_optimization": rl_result,
        "planning_evaluation": planning_result,
        "status": "completed",
    }

    logger.info("RL optimization flow completed")
    return final_result


@flow
def rl_training_flow(feedback_data: list, training_steps: int = 5000):
    """Train RL model based on user feedback"""
    logger = get_run_logger()
    logger.info(f"Starting RL training with {len(feedback_data)} feedback entries")

    # Process feedback for training parameters
    avg_rating = sum(f.get("rating", 0) for f in feedback_data) / max(len(feedback_data), 1)

    # Adjust training parameters based on feedback
    training_params = {
        "learning_rate": 3e-4 * (avg_rating / 5.0),  # Scale by feedback quality
        "batch_size": min(2048, len(feedback_data) * 64),
        "n_epochs": 10,
    }

    # Train model
    training_result = train_rl_model(training_steps, **training_params)

    result = {
        "feedback_processed": len(feedback_data),
        "average_rating": avg_rating,
        "training_result": training_result,
        "status": "completed",
    }

    logger.info("RL training flow completed")
    return result
