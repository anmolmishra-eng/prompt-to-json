"""
Prefect Flow: Log Aggregation & Monitoring
Replaces N8N log aggregation workflow
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from prefect import flow, task
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LogConfig(BaseModel):
    """Configuration for log aggregation"""

    log_sources: List[Path] = [Path("logs/task7"), Path("logs/sohum_mcp"), Path("logs/ranjeet_rl"), Path("logs/bhiv")]
    output_dir: Path = Path("reports/logs")
    retention_days: int = 30


@task(name="collect-logs-from-sources")
def collect_logs_from_sources(sources: List[Path]) -> Dict[str, List[str]]:
    """
    Collect logs from all system sources
    """
    collected_logs = {}

    for source in sources:
        source_name = source.name

        if not source.exists():
            logger.warning(f"Log source not found: {source}")
            collected_logs[source_name] = []
            continue

        # Collect log files from last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)

        log_files = []
        for log_file in source.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff:
                log_files.append(str(log_file))

        collected_logs[source_name] = log_files
        logger.info(f"Collected {len(log_files)} log files from {source_name}")

    return collected_logs


@task(name="parse-error-logs")
def parse_error_logs(log_files: List[str]) -> Dict:
    """
    Parse logs for errors and warnings
    """
    errors = []
    warnings = []

    for log_file_path in log_files:
        try:
            with open(log_file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    if "ERROR" in line:
                        errors.append({"file": Path(log_file_path).name, "line": line_num, "message": line.strip()})
                    elif "WARNING" in line:
                        warnings.append({"file": Path(log_file_path).name, "line": line_num, "message": line.strip()})

        except Exception as e:
            logger.error(f"Failed to parse {log_file_path}: {e}")

    return {"errors": errors, "warnings": warnings, "error_count": len(errors), "warning_count": len(warnings)}


@task(name="generate-log-report")
def generate_log_report(collected_logs: Dict[str, List[str]], error_analysis: Dict, output_dir: Path) -> Path:
    """
    Generate aggregated log report
    """
    import json

    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / f"log_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "sources": {source: len(files) for source, files in collected_logs.items()},
        "error_summary": {
            "total_errors": error_analysis["error_count"],
            "total_warnings": error_analysis["warning_count"],
            "errors": error_analysis["errors"][:10],  # Top 10 errors
            "warnings": error_analysis["warnings"][:10],  # Top 10 warnings
        },
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Log report saved to {report_file}")

    return report_file


@task(name="send-alert-if-errors")
async def send_alert_if_errors(error_analysis: Dict, threshold: int = 10):
    """
    Send alert if error count exceeds threshold
    """
    error_count = error_analysis["error_count"]

    if error_count > threshold:
        logger.warning(f"⚠️ HIGH ERROR COUNT: {error_count} errors detected!")

        # TODO: Send email/Slack notification
        # For now, just log
        logger.info(f"Alert would be sent (threshold: {threshold}, actual: {error_count})")

        return {"alert_sent": True, "error_count": error_count, "threshold": threshold}

    return {"alert_sent": False, "error_count": error_count, "threshold": threshold}


@flow(
    name="log-aggregation-and-monitoring",
    description="Aggregate logs from all systems and generate reports",
    version="1.0",
)
async def log_aggregation_flow(config: LogConfig = LogConfig()):
    """
    Main flow: Collect logs → Parse errors → Generate report → Send alerts

    Replaces N8N log aggregation workflow
    """
    logger.info("Starting log aggregation flow...")

    # Step 1: Collect logs
    collected_logs = collect_logs_from_sources(config.log_sources)

    # Step 2: Parse all logs for errors
    all_log_files = []
    for files in collected_logs.values():
        all_log_files.extend(files)

    error_analysis = parse_error_logs(all_log_files)

    # Step 3: Generate report
    report_file = generate_log_report(collected_logs, error_analysis, config.output_dir)

    # Step 4: Send alerts if needed
    alert_result = await send_alert_if_errors(error_analysis, threshold=10)

    logger.info("Log aggregation flow complete")

    return {
        "status": "complete",
        "report_file": str(report_file),
        "error_count": error_analysis["error_count"],
        "warning_count": error_analysis["warning_count"],
        "alert_sent": alert_result["alert_sent"],
    }


# Schedule configuration for deployment
# Use cron or interval in deployment script


# Deployment
if __name__ == "__main__":
    asyncio.run(log_aggregation_flow())
