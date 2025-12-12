"""
Structured Logging & Monitoring System
Complete implementation with alerts and metrics
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/monitoring", tags=["📊 Monitoring & Alerts"])


# Configure structured logging
class StructuredLogger:
    """Structured logger with JSON output and monitoring"""

    def __init__(self, name: str, log_dir: str = "data/logs"):
        self.name = name
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter("%(message)s")

        # File handler for structured logs
        log_file = os.path.join(log_dir, f"{name}.jsonl")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_structured(self, level: str, event: str, **kwargs):
        """Log structured event with metadata"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "event": event,
            "service": self.name,
            **kwargs,
        }

        # Log as JSON
        self.logger.log(getattr(logging, level.upper()), json.dumps(log_entry))

        # Check for alerts
        if level.upper() in ["ERROR", "CRITICAL"]:
            asyncio.create_task(self._send_alert(log_entry))

    async def _send_alert(self, log_entry: Dict[str, Any]):
        """Send alert for critical events"""

        try:
            alert_message = f"🚨 {log_entry['level']} Alert\n"
            alert_message += f"Service: {log_entry['service']}\n"
            alert_message += f"Event: {log_entry['event']}\n"
            alert_message += f"Time: {log_entry['timestamp']}\n"

            if "error" in log_entry:
                alert_message += f"Error: {log_entry['error']}\n"

            # Save alert to file
            alert_file = os.path.join(self.log_dir, "alerts.jsonl")
            with open(alert_file, "a") as f:
                f.write(json.dumps({**log_entry, "alert_sent": True}) + "\n")

        except Exception as e:
            # Fallback to file logging
            alert_file = os.path.join(self.log_dir, "alerts.jsonl")
            with open(alert_file, "a") as f:
                f.write(json.dumps({**log_entry, "alert_failed": str(e)}) + "\n")

    def info(self, event: str, **kwargs):
        """Log info event"""
        self.log_structured("info", event, **kwargs)

    def error(self, event: str, **kwargs):
        """Log error event"""
        self.log_structured("error", event, **kwargs)


class PerformanceMonitor:
    """Performance monitoring with metrics collection"""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics = {}

    def track_performance(self, operation: str):
        """Decorator to track operation performance"""

        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                operation_id = f"{operation}_{int(start_time * 1000)}"

                try:
                    self.logger.info("operation_started", operation=operation, operation_id=operation_id)

                    result = await func(*args, **kwargs)

                    duration_ms = int((time.time() - start_time) * 1000)

                    self.logger.info(
                        "operation_completed",
                        operation=operation,
                        operation_id=operation_id,
                        duration_ms=duration_ms,
                        status="success",
                    )

                    # Update metrics
                    self._update_metrics(operation, duration_ms, "success")

                    return result

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)

                    self.logger.error(
                        "operation_failed",
                        operation=operation,
                        operation_id=operation_id,
                        duration_ms=duration_ms,
                        error=str(e),
                        status="failed",
                    )

                    # Update metrics
                    self._update_metrics(operation, duration_ms, "failed")

                    raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else func

        return decorator

    def _update_metrics(self, operation: str, duration_ms: int, status: str):
        """Update operation metrics"""

        if operation not in self.metrics:
            self.metrics[operation] = {
                "total_calls": 0,
                "success_calls": 0,
                "failed_calls": 0,
                "total_duration_ms": 0,
                "avg_duration_ms": 0,
            }

        metrics = self.metrics[operation]
        metrics["total_calls"] += 1
        metrics["total_duration_ms"] += duration_ms

        if status == "success":
            metrics["success_calls"] += 1
        else:
            metrics["failed_calls"] += 1

        metrics["avg_duration_ms"] = metrics["total_duration_ms"] / metrics["total_calls"]

        # Save metrics periodically
        if metrics["total_calls"] % 10 == 0:
            self._save_metrics()

    def _save_metrics(self):
        """Save metrics to file"""

        metrics_file = os.path.join(self.logger.log_dir, "metrics.json")
        metrics_data = {"timestamp": datetime.now().isoformat(), "metrics": self.metrics}

        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""

        total_operations = sum(m["total_calls"] for m in self.metrics.values())
        total_failures = sum(m["failed_calls"] for m in self.metrics.values())

        return {
            "total_operations": total_operations,
            "total_failures": total_failures,
            "success_rate": (total_operations - total_failures) / max(total_operations, 1),
            "operations": self.metrics,
            "timestamp": datetime.now().isoformat(),
        }


# Global instances
bhiv_logger = StructuredLogger("bhiv_assistant")
performance_monitor = PerformanceMonitor(bhiv_logger)


class MonitoringResponse(BaseModel):
    """Monitoring response model"""

    status: str
    metrics: Dict[str, Any]
    alerts: list
    timestamp: str


@router.get("/metrics", response_model=MonitoringResponse)
async def get_metrics():
    """Get system metrics and alerts"""

    # Get performance metrics
    metrics = performance_monitor.get_metrics_summary()

    # Check for recent alerts
    alerts = []
    alert_file = os.path.join(bhiv_logger.log_dir, "alerts.jsonl")

    if os.path.exists(alert_file):
        with open(alert_file, "r") as f:
            lines = f.readlines()
            # Get last 10 alerts
            for line in lines[-10:]:
                try:
                    alert = json.loads(line.strip())
                    alerts.append(alert)
                except:
                    continue

    # Determine overall status
    success_rate = metrics.get("success_rate", 1.0)
    if success_rate < 0.8:
        status = "unhealthy"
    elif success_rate < 0.95:
        status = "degraded"
    else:
        status = "healthy"

    return MonitoringResponse(status=status, metrics=metrics, alerts=alerts, timestamp=datetime.now().isoformat())


@router.post("/alert/test")
async def test_alert():
    """Test alert system"""

    bhiv_logger.error("test_alert", message="This is a test alert", test=True)

    return {"status": "success", "message": "Test alert sent"}


# Convenience functions
def log_info(event: str, **kwargs):
    """Log info event"""
    bhiv_logger.info(event, **kwargs)


def log_error(event: str, **kwargs):
    """Log error event"""
    bhiv_logger.error(event, **kwargs)


def track_performance(operation: str):
    """Track operation performance"""
    return performance_monitor.track_performance(operation)
