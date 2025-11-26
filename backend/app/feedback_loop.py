"""
Feedback loop integration between user evaluations and RL training.
Converts user feedback into training data for iterative model improvement.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from app.models import Evaluation, Iteration, RLFeedback, Spec
from app.rl import rl_feedback as rl_feedback_endpoint
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class FeedbackLoopOrchestrator:
    """Orchestrates feedback collection and feeds it into RL training pipeline"""

    def __init__(self, db: Session):
        self.db = db
        self.min_feedback_pairs = 10  # Minimum pairs before triggering training

    def collect_user_feedback(self, user_id: str, spec_id: str, rating: float, notes: str) -> dict:
        """
        Collect user feedback and store as RLHF preference data.

        Args:
            user_id: User identifier
            spec_id: Spec being evaluated
            rating: User rating (0-5)
            notes: User feedback notes

        Returns:
            Feedback collection metadata
        """

        # Get spec details
        spec = self.db.query(Spec).filter(Spec.spec_id == spec_id).first()
        if not spec:
            raise ValueError(f"Spec {spec_id} not found")

        logger.info(f"Collecting feedback from {user_id} for spec {spec_id}: rating={rating}")

        # Find related iterations for this spec (to build preference pairs)
        iterations = self.db.query(Iteration).filter(Iteration.spec_id == spec_id).order_by(Iteration.ts).all()

        feedback_pairs = []

        # Create preference pairs: before_spec vs after_spec
        if len(iterations) >= 2:
            for i in range(len(iterations) - 1):
                before_iter = iterations[i]
                after_iter = iterations[i + 1]

                # Preference: higher rated spec is preferred
                # Assume later iterations are improvements
                preference = "B" if rating > 3 else ("A" if rating < 3 else "EQUAL")

                feedback = RLFeedback(
                    user_id=user_id,
                    spec_id=spec_id,
                    prompt=spec.prompt,
                    spec_json=spec.spec_json,
                    user_rating=rating,
                    feedback_type="explicit",
                )

                self.db.add(feedback)
                feedback_pairs.append(
                    {"before": before_iter.iter_id, "after": after_iter.iter_id, "preference": preference}
                )

        # Store the primary evaluation feedback
        rlhf_fb = RLFeedback(
            user_id=user_id,
            spec_id=spec_id,
            prompt=spec.prompt,
            spec_json=spec.spec_json,
            user_rating=rating,
            feedback_type="explicit",
        )

        self.db.add(rlhf_fb)
        self.db.commit()

        logger.info(f"Stored {len(feedback_pairs)} preference pairs from user feedback")

        return {"feedback_id": rlhf_fb.id, "pairs_created": len(feedback_pairs), "spec_id": spec_id, "user_id": user_id}

    def aggregate_feedback(self, lookback_hours: int = 24) -> dict:
        """
        Aggregate recent feedback to identify patterns and training needs.

        Args:
            lookback_hours: How many hours of feedback to look back

        Returns:
            Aggregated feedback statistics
        """

        from datetime import timedelta

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

        # Get recent evaluations
        recent_evals = self.db.query(Evaluation).filter(Evaluation.ts >= cutoff_time).all()

        # Get recent RL feedback
        recent_feedback = self.db.query(RLFeedback).filter(RLFeedback.created_at >= cutoff_time).all()

        # Calculate statistics
        total_feedback = len(recent_evals) + len(recent_feedback)
        avg_rating = sum(e.score for e in recent_evals if e.score) / len(recent_evals) if recent_evals else 0

        # Count feedback type distribution
        feedback_counts = {
            "explicit": len([fb for fb in recent_feedback if fb.feedback_type == "explicit"]),
            "implicit": len([fb for fb in recent_feedback if fb.feedback_type == "implicit"]),
        }

        logger.info(
            f"Aggregated feedback: {total_feedback} items, "
            f"avg_rating: {avg_rating:.2f}, preferences: {preference_counts}"
        )

        return {
            "total_feedback": total_feedback,
            "average_rating": avg_rating,
            "evaluation_count": len(recent_evals),
            "feedback_count": len(recent_feedback),
            "feedback_distribution": feedback_counts,
            "lookback_hours": lookback_hours,
            "cutoff_time": cutoff_time.isoformat(),
        }

    def should_trigger_training(self) -> Tuple[bool, dict]:
        """
        Determine if enough feedback has accumulated to trigger RL training.

        Returns:
            (should_train: bool, stats: dict)
        """

        # Count total feedback in database
        total_feedback = self.db.query(RLFeedback).count()

        should_train = total_feedback >= self.min_feedback_pairs

        stats = {
            "total_feedback_records": total_feedback,
            "min_required": self.min_feedback_pairs,
            "ready_for_training": should_train,
        }

        if should_train:
            logger.info("Sufficient feedback accumulated - ready for RL training")

        return should_train, stats

    def create_training_dataset(self, limit: Optional[int] = None) -> List[dict]:
        """
        Create training dataset from accumulated feedback.

        Args:
            limit: Maximum number of pairs to include

        Returns:
            List of preference pairs formatted for training
        """

        # Get feedback records
        feedback_records = self.db.query(RLFeedback).limit(limit).all()

        dataset = []
        for fb in feedback_records:
            dataset.append(
                {
                    "prompt": fb.prompt,
                    "spec_json": fb.spec_json,
                    "user_rating": fb.user_rating,
                    "user_id": fb.user_id,
                    "feedback_type": fb.feedback_type,
                    "timestamp": fb.created_at.isoformat() if fb.created_at else None,
                }
            )

        logger.info(f"Created training dataset with {len(dataset)} pairs")

        return dataset

    def get_feedback_quality_metrics(self) -> dict:
        """Calculate metrics about feedback quality and completeness"""

        all_evals = self.db.query(Evaluation).all()
        all_feedback = self.db.query(RLFeedback).all()

        # Quality metrics
        evals_with_notes = len([e for e in all_evals if e.notes])
        explicit_feedback = len([f for f in all_feedback if f.feedback_type == "explicit"])

        # Rating distribution
        rating_dist = {}
        for eval in all_evals:
            if eval.rating:
                bucket = int(eval.rating)
                rating_dist[bucket] = rating_dist.get(bucket, 0) + 1

        metrics = {
            "total_evaluations": len(all_evals),
            "total_feedback": len(all_feedback),
            "evals_with_notes": evals_with_notes,
            "explicit_feedback": explicit_feedback,
            "avg_notes_rate": evals_with_notes / len(all_evals) if all_evals else 0,
            "rating_distribution": rating_dist,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return metrics


class IterativeFeedbackCycle:
    """Manages the iterative feedback-training-improvement cycle"""

    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = FeedbackLoopOrchestrator(db)

    async def process_evaluation_feedback(self, user_id: str, spec_id: str, rating: float, notes: str) -> dict:
        """
        Process user evaluation and potentially trigger training cycle.

        Returns:
            Status of feedback processing and any triggered actions
        """

        # 1. Collect feedback
        feedback_result = self.orchestrator.collect_user_feedback(user_id, spec_id, rating, notes)

        # 2. Check if training should be triggered
        should_train, train_stats = self.orchestrator.should_trigger_training()

        result = {
            "feedback_collected": feedback_result,
            "training_triggered": should_train,
            "training_stats": train_stats,
        }

        # 3. If ready, trigger async training job
        if should_train:
            logger.info("Triggering RL training from accumulated feedback")
            result["training_queued"] = True

            # In production, queue this as an async job
            # For now, just log it
            train_data = self.orchestrator.create_training_dataset(limit=50)
            result["dataset_size"] = len(train_data)

        return result

    def get_cycle_status(self) -> dict:
        """Get current status of the feedback-training cycle"""

        stats = self.orchestrator.aggregate_feedback()
        should_train, train_stats = self.orchestrator.should_trigger_training()
        quality = self.orchestrator.get_feedback_quality_metrics()

        return {
            "cycle_status": "ready_for_training" if should_train else "collecting_feedback",
            "feedback_stats": stats,
            "training_readiness": train_stats,
            "quality_metrics": quality,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
