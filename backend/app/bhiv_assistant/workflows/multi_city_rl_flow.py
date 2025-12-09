import json
import os

from prefect import flow, get_run_logger, task


@task
def load_city_dataset(city: str) -> dict:
    """Load city-specific dataset (e.g., DCPR 2034, local maps)"""
    # Mock city data - in practice, load from database or files
    city_datasets = {
        "Mumbai": {"dcr": "DCPR_2034", "population": 12442373, "area_sqkm": 603},
        "Pune": {"dcr": "Pune_DCR", "population": 3124458, "area_sqkm": 331},
        "Nashik": {"dcr": "Nashik_DCR", "population": 1486973, "area_sqkm": 264},
        "Ahmedabad": {"dcr": "Ahmedabad_DCR", "population": 5570585, "area_sqkm": 505},
    }

    logger = get_run_logger()
    logger.info(f"Loading dataset for {city}")
    return city_datasets.get(city, {"dcr": "Generic_DCR", "population": 1000000, "area_sqkm": 100})


@task
def apply_mcp_rules(city_data: dict) -> dict:
    """Apply MCP compliance rules to city data"""
    # Mock compliance check
    compliance_result = {
        "compliant": True,
        "violations": [],
        "dcr_applied": city_data.get("dcr", "Generic_DCR"),
        "population_density": city_data.get("population", 0) / city_data.get("area_sqkm", 1),
    }

    logger = get_run_logger()
    logger.info(f"Applied MCP rules: {compliance_result}")
    return compliance_result


@task
def run_rl_model(city: str, compliance_data: dict) -> dict:
    """
    Run the RL agent for the given city using existing model code.
    """
    # Mock RL model - in practice, integrate with Ranjeet's system
    try:
        # Simulate RL optimization
        output = {
            "city": city,
            "optimization_type": "land_use",
            "compliance_score": compliance_data.get("population_density", 0) / 10000,
            "recommendations": [
                "Increase residential density in zone A",
                "Add commercial spaces near transport hubs",
                "Preserve green corridors",
            ],
            "confidence": 0.87,
            "iterations": 1000,
            "geometry_url": f"/api/v1/geometry/{city.lower()}_optimized.glb",
        }

        logger = get_run_logger()
        logger.info(f"RL model output for {city}: {output}")
        return output

    except Exception as e:
        logger.error(f"RL model failed for {city}: {e}")
        return {"error": str(e), "city": city}


@task
def save_json(data: dict, output_path: str):
    """Save the given data dict as JSON to the specified path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    logger = get_run_logger()
    logger.info(f"Saved output JSON to {output_path}")


@flow(name="Multi_City_RL_Workflow")
def multi_city_rl_flow(cities: list = ["Mumbai", "Pune", "Nashik", "Ahmedabad"]):
    """
    Integrate multi-city datasets and run RL agent for each city (Day 4 tasks).
    """
    results = {}

    for city in cities:
        # Load city-specific dataset
        city_data = load_city_dataset(city)

        # Apply compliance rules
        compliance = apply_mcp_rules(city_data)

        # Run RL model
        rl_result = run_rl_model(city, compliance)

        # Save results
        save_json(rl_result, f"data/{city}_rl_result.json")

        results[city] = rl_result

    return results


@task
def process_feedback(feedback_file: str = "data/feedback_log.jsonl") -> dict:
    """Process user feedback for RL model updates"""
    feedback_data = []

    if os.path.exists(feedback_file):
        with open(feedback_file, "r") as f:
            for line in f:
                try:
                    feedback_data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

    # Aggregate feedback
    total_feedback = len(feedback_data)
    avg_rating = sum(f.get("rating", 0) for f in feedback_data) / max(total_feedback, 1)

    logger = get_run_logger()
    logger.info(f"Processed {total_feedback} feedback entries, avg rating: {avg_rating}")

    return {"total_feedback": total_feedback, "average_rating": avg_rating, "feedback_data": feedback_data}


@task
def update_rl_model(feedback_summary: dict) -> dict:
    """Update RL model weights based on feedback"""
    # Mock model update - in practice, call Ranjeet's model update method
    if feedback_summary["total_feedback"] > 0:
        update_result = {
            "model_updated": True,
            "feedback_processed": feedback_summary["total_feedback"],
            "new_learning_rate": 0.001 * (feedback_summary["average_rating"] / 5.0),
            "update_timestamp": "2024-12-05T20:00:00Z",
        }
    else:
        update_result = {"model_updated": False, "reason": "No feedback available"}

    logger = get_run_logger()
    logger.info(f"RL model update result: {update_result}")
    return update_result


@flow(name="RL_Feedback_Loop_Workflow")
def rl_feedback_loop_flow():
    """
    Reinforcement learning feedback loop - process user feedback and update model.
    """
    # Process accumulated feedback
    feedback_summary = process_feedback()

    # Update RL model based on feedback
    update_result = update_rl_model(feedback_summary)

    # Save update results
    save_json(update_result, "data/rl_model_updates.json")

    return {"feedback_summary": feedback_summary, "update_result": update_result}
