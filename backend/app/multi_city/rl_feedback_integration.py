"""
Multi-City RL Feedback Loop Integration
Connects city-specific rules with RL training
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MultiCityRLFeedback:
    """Multi-city RL feedback loop manager"""

    SUPPORTED_CITIES = ["Mumbai", "Pune", "Ahmedabad", "Nashik", "Bangalore"]

    def __init__(self):
        self.feedback_storage = "data/rl_feedback"
        os.makedirs(self.feedback_storage, exist_ok=True)

    async def collect_city_feedback(
        self, city: str, design_spec: Dict[str, Any], user_rating: float, compliance_result: Dict[str, Any]
    ) -> str:
        """Collect feedback for city-specific RL training"""

        feedback_entry = {
            "feedback_id": f"fb_{city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "city": city,
            "timestamp": datetime.now().isoformat(),
            "design_spec": design_spec,
            "user_rating": user_rating,
            "compliance_result": compliance_result,
            "city_specific_metrics": self._extract_city_metrics(city, design_spec, compliance_result),
        }

        # Store feedback by city
        city_feedback_file = os.path.join(self.feedback_storage, f"{city.lower()}_feedback.jsonl")
        with open(city_feedback_file, "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        logger.info(f"Collected RL feedback for {city}: {feedback_entry['feedback_id']}")

        # Check if enough feedback for training
        await self._check_training_threshold(city)

        return feedback_entry["feedback_id"]

    def _extract_city_metrics(
        self, city: str, design_spec: Dict[str, Any], compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract city-specific metrics for RL training"""

        metrics = {
            "compliance_score": compliance_result.get("confidence_score", 0.0),
            "violations_count": len(compliance_result.get("violations", [])),
            "city_rules_applied": compliance_result.get("rules_applied", []),
        }

        # City-specific metric extraction
        if city == "Mumbai":
            metrics.update(
                {
                    "fsi_compliance": self._check_fsi_mumbai(design_spec),
                    "coastal_zone_check": self._check_coastal_zone(design_spec),
                    "high_rise_compliance": self._check_high_rise_mumbai(design_spec),
                }
            )
        elif city == "Pune":
            metrics.update(
                {
                    "pmc_compliance": self._check_pmc_rules(design_spec),
                    "hill_station_rules": self._check_hill_station_rules(design_spec),
                    "water_harvesting": self._check_water_harvesting(design_spec),
                }
            )
        elif city == "Ahmedabad":
            metrics.update(
                {
                    "amc_compliance": self._check_amc_rules(design_spec),
                    "earthquake_resistance": self._check_earthquake_resistance(design_spec),
                    "heat_island_mitigation": self._check_heat_island(design_spec),
                }
            )

        return metrics

    def _check_fsi_mumbai(self, design_spec: Dict[str, Any]) -> float:
        """Check FSI compliance for Mumbai"""
        plot_area = design_spec.get("plot_area", 1000)
        built_area = design_spec.get("built_area", 800)
        return min(built_area / plot_area, 1.33)  # Mumbai FSI limit

    def _check_coastal_zone(self, design_spec: Dict[str, Any]) -> bool:
        """Check coastal zone regulations"""
        location = design_spec.get("location", {})
        if isinstance(location, str):
            return "coastal" in location.lower() or "marine" in location.lower()
        elif isinstance(location, dict):
            return location.get("coastal_zone", False)
        return False

    def _check_high_rise_mumbai(self, design_spec: Dict[str, Any]) -> bool:
        """Check high-rise compliance for Mumbai"""
        height = design_spec.get("building_height", 0)
        return height <= 70  # Mumbai height limit in meters

    def _check_pmc_rules(self, design_spec: Dict[str, Any]) -> float:
        """Check PMC compliance for Pune"""
        return 0.85  # Placeholder

    def _check_hill_station_rules(self, design_spec: Dict[str, Any]) -> bool:
        """Check hill station rules for Pune"""
        return True  # Placeholder

    def _check_water_harvesting(self, design_spec: Dict[str, Any]) -> bool:
        """Check water harvesting requirements"""
        return design_spec.get("water_harvesting", False)

    def _check_amc_rules(self, design_spec: Dict[str, Any]) -> float:
        """Check AMC compliance for Ahmedabad"""
        return 0.80  # Placeholder

    def _check_earthquake_resistance(self, design_spec: Dict[str, Any]) -> bool:
        """Check earthquake resistance for Ahmedabad"""
        return design_spec.get("earthquake_resistant", False)

    def _check_heat_island(self, design_spec: Dict[str, Any]) -> bool:
        """Check heat island mitigation"""
        return design_spec.get("green_roof", False) or design_spec.get("reflective_surfaces", False)

    async def _check_training_threshold(self, city: str):
        """Check if enough feedback collected for RL training"""

        city_feedback_file = os.path.join(self.feedback_storage, f"{city.lower()}_feedback.jsonl")

        if not os.path.exists(city_feedback_file):
            return

        with open(city_feedback_file, "r") as f:
            feedback_count = len(f.readlines())

        # Trigger training if threshold reached
        if feedback_count >= 50:  # 50 feedback entries threshold
            logger.info(f"Training threshold reached for {city}: {feedback_count} entries")
            await self._trigger_rl_training(city)

    async def _trigger_rl_training(self, city: str):
        """Trigger RL training for specific city"""

        try:
            # Load city-specific feedback
            feedback_data = self._load_city_feedback(city)

            # Call RL training endpoint
            import httpx

            async with httpx.AsyncClient(timeout=300.0) as client:
                training_payload = {
                    "city": city,
                    "feedback_data": feedback_data,
                    "training_type": "city_specific",
                    "model_name": f"rl_model_{city.lower()}",
                }

                try:
                    response = await client.post(
                        "http://localhost:8000/api/v1/rl/train/city_specific", json=training_payload
                    )
                    response.raise_for_status()

                    logger.info(f"RL training triggered for {city}")

                except Exception as e:
                    logger.error(f"RL training failed for {city}: {e}")

        except Exception as e:
            logger.error(f"Failed to trigger RL training for {city}: {e}")

    def _load_city_feedback(self, city: str) -> List[Dict[str, Any]]:
        """Load feedback data for specific city"""

        city_feedback_file = os.path.join(self.feedback_storage, f"{city.lower()}_feedback.jsonl")
        feedback_data = []

        if os.path.exists(city_feedback_file):
            with open(city_feedback_file, "r") as f:
                for line in f:
                    feedback_data.append(json.loads(line.strip()))

        return feedback_data

    async def get_city_feedback_summary(self, city: str) -> Dict[str, Any]:
        """Get feedback summary for specific city"""

        feedback_data = self._load_city_feedback(city)

        if not feedback_data:
            return {"city": city, "feedback_count": 0, "average_rating": 0.0}

        total_rating = sum(entry["user_rating"] for entry in feedback_data)
        avg_rating = total_rating / len(feedback_data)

        recent_feedback = [
            entry
            for entry in feedback_data
            if datetime.fromisoformat(entry["timestamp"]) > datetime.now().replace(day=datetime.now().day - 7)
        ]

        return {
            "city": city,
            "feedback_count": len(feedback_data),
            "average_rating": avg_rating,
            "recent_feedback_count": len(recent_feedback),
            "last_training": self._get_last_training_date(city),
        }

    def _get_last_training_date(self, city: str) -> str:
        """Get last training date for city"""
        training_log = os.path.join(self.feedback_storage, f"{city.lower()}_training.log")

        if os.path.exists(training_log):
            with open(training_log, "r") as f:
                lines = f.readlines()
                if lines:
                    return lines[-1].strip().split(":")[0]

        return "Never"


# Global instance
multi_city_rl = MultiCityRLFeedback()
