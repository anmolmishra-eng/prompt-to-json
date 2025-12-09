import json
import os
from datetime import datetime

from prefect import flow, get_run_logger, task
from prefect.context import get_run_context


@task
def notify_slack_on_error(message: str):
    """Send an alert to Slack."""
    # Mock Slack notification - in practice, use prefect-slack
    logger = get_run_logger()
    logger.error(f"SLACK ALERT: {message}")

    # Save alert to file for monitoring
    alert_data = {"timestamp": datetime.now().isoformat(), "message": message, "channel": "#alerts", "type": "error"}

    os.makedirs("data/alerts", exist_ok=True)
    with open("data/alerts/slack_alerts.jsonl", "a") as f:
        f.write(json.dumps(alert_data) + "\n")


@task
def notify_email_on_error(message: str, recipients: list = ["admin@bhiv.com"]):
    """Send email notification on error."""
    # Mock email notification - in practice, use prefect-email
    logger = get_run_logger()
    logger.error(f"EMAIL ALERT to {recipients}: {message}")

    # Save email alert to file
    email_data = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "recipients": recipients,
        "type": "error",
    }

    os.makedirs("data/alerts", exist_ok=True)
    with open("data/alerts/email_alerts.jsonl", "a") as f:
        f.write(json.dumps(email_data) + "\n")


@task
def log_success(flow_name: str, duration: float, details: dict = None):
    """Log successful flow execution."""
    success_data = {
        "timestamp": datetime.now().isoformat(),
        "flow_name": flow_name,
        "status": "success",
        "duration_seconds": duration,
        "details": details or {},
    }

    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/success_log.jsonl", "a") as f:
        f.write(json.dumps(success_data) + "\n")

    logger = get_run_logger()
    logger.info(f"SUCCESS: {flow_name} completed in {duration:.2f}s")


@task
def log_failure(flow_name: str, error: str, context: dict = None):
    """Log failed flow execution."""
    failure_data = {
        "timestamp": datetime.now().isoformat(),
        "flow_name": flow_name,
        "status": "failure",
        "error": error,
        "context": context or {},
    }

    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/failure_log.jsonl", "a") as f:
        f.write(json.dumps(failure_data) + "\n")

    logger = get_run_logger()
    logger.error(f"FAILURE: {flow_name} failed with error: {error}")


@flow(name="MCP_Workflow_With_Alerts")
def mcp_flow_with_alerts():
    """MCP workflow with error handling and alerts."""
    import time

    start_time = time.time()
    flow_name = "MCP_Workflow_With_Alerts"

    try:
        # Import and run MCP compliance flow
        from mcp_compliance_flow import mcp_compliance_flow

        logger = get_run_logger()
        logger.info(f"Starting {flow_name}")

        # Run the actual workflow
        result = mcp_compliance_flow()

        # Log success
        duration = time.time() - start_time
        log_success(flow_name, duration, {"result": "MCP compliance completed"})

        return {"status": "success", "duration": duration}

    except Exception as e:
        # Log failure
        duration = time.time() - start_time
        error_msg = str(e)
        log_failure(flow_name, error_msg, {"duration": duration})

        # Send alerts
        notify_slack_on_error(f"MCP flow failed: {error_msg}")
        notify_email_on_error(f"MCP Compliance Workflow failed: {error_msg}")

        # Re-raise to maintain Prefect error handling
        raise


@flow(name="RL_Workflow_With_Alerts")
def rl_flow_with_alerts():
    """RL workflow with error handling and alerts."""
    import time

    start_time = time.time()
    flow_name = "RL_Workflow_With_Alerts"

    try:
        # Import and run RL flow
        from multi_city_rl_flow import multi_city_rl_flow

        logger = get_run_logger()
        logger.info(f"Starting {flow_name}")

        # Run the actual workflow
        result = multi_city_rl_flow()

        # Log success
        duration = time.time() - start_time
        cities_processed = len(result) if isinstance(result, dict) else 0
        log_success(flow_name, duration, {"cities_processed": cities_processed})

        return {"status": "success", "duration": duration, "cities": cities_processed}

    except Exception as e:
        # Log failure
        duration = time.time() - start_time
        error_msg = str(e)
        log_failure(flow_name, error_msg, {"duration": duration})

        # Send alerts
        notify_slack_on_error(f"RL flow failed: {error_msg}")
        notify_email_on_error(f"Multi-City RL Workflow failed: {error_msg}")

        # Re-raise to maintain Prefect error handling
        raise


@task
def generate_monitoring_report() -> dict:
    """Generate monitoring report from logs."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "success_count": 0,
        "failure_count": 0,
        "alert_count": 0,
        "recent_failures": [],
    }

    # Count successes
    if os.path.exists("data/logs/success_log.jsonl"):
        with open("data/logs/success_log.jsonl", "r") as f:
            report["success_count"] = len(f.readlines())

    # Count failures
    if os.path.exists("data/logs/failure_log.jsonl"):
        with open("data/logs/failure_log.jsonl", "r") as f:
            lines = f.readlines()
            report["failure_count"] = len(lines)
            # Get recent failures (last 5)
            for line in lines[-5:]:
                try:
                    failure = json.loads(line.strip())
                    report["recent_failures"].append(failure)
                except json.JSONDecodeError:
                    continue

    # Count alerts
    if os.path.exists("data/alerts/slack_alerts.jsonl"):
        with open("data/alerts/slack_alerts.jsonl", "r") as f:
            report["alert_count"] = len(f.readlines())

    return report


@flow(name="System_Monitoring_Workflow")
def system_monitoring_flow():
    """Generate system monitoring report."""
    logger = get_run_logger()
    logger.info("Generating system monitoring report")

    report = generate_monitoring_report()

    # Save report
    os.makedirs("data/reports", exist_ok=True)
    with open("data/reports/monitoring_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Alert if too many failures
    if report["failure_count"] > 5:
        notify_slack_on_error(f"High failure rate detected: {report['failure_count']} failures")

    logger.info(f"Monitoring report: {report['success_count']} successes, {report['failure_count']} failures")
    return report
