import json
import os
from datetime import datetime

from prefect import flow, get_run_logger, task
from prefect.blocks.notifications import SlackWebhook


@task
def send_slack_notification(message: str, subject: str = "BHIV Alert"):
    """Send Slack notification"""
    logger = get_run_logger()

    try:
        # Try to load Slack webhook block
        slack = SlackWebhook.load("bhiv-slack-webhook")
        slack.notify(body=message, subject=subject)
        logger.info(f"Slack notification sent: {subject}")
    except Exception as e:
        # Fallback to file logging
        logger.warning(f"Slack notification failed: {e}")

        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "slack_alert",
            "subject": subject,
            "message": message,
            "status": "fallback_logged",
        }

        os.makedirs("data/alerts", exist_ok=True)
        with open("data/alerts/slack_notifications.jsonl", "a") as f:
            f.write(json.dumps(alert_data) + "\n")


@task
def send_email_notification(message: str, subject: str = "BHIV Alert", recipients: list = None):
    """Send email notification"""
    logger = get_run_logger()

    if recipients is None:
        recipients = ["admin@bhiv.com"]

    try:
        # Try to load email block
        from prefect.blocks.notifications import EmailServerCredentials

        email_block = EmailServerCredentials.load("bhiv-email-credentials")
        email_block.notify(body=message, subject=subject)
        logger.info(f"Email notification sent to {recipients}")
    except Exception as e:
        # Fallback to file logging
        logger.warning(f"Email notification failed: {e}")

        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "email_alert",
            "subject": subject,
            "message": message,
            "recipients": recipients,
            "status": "fallback_logged",
        }

        os.makedirs("data/alerts", exist_ok=True)
        with open("data/alerts/email_notifications.jsonl", "a") as f:
            f.write(json.dumps(alert_data) + "\n")


@flow
def monitored_rl_flow(prompt: str, city: str = "Mumbai"):
    """RL flow with monitoring and notifications"""
    logger = get_run_logger()
    flow_name = "monitored_rl_flow"

    try:
        logger.info(f"Starting {flow_name} for {city}: {prompt}")

        # Import and run RL optimization
        from rl_integration_flows import rl_optimization_flow

        result = rl_optimization_flow(prompt, city)

        # Success notification
        success_msg = f"RL optimization completed successfully for {city}"
        logger.info(success_msg)

        return result

    except Exception as e:
        # Error notifications
        error_msg = f"RL flow failed for {city}: {str(e)}"
        logger.error(error_msg)

        # Send alerts
        send_slack_notification(error_msg, "RL Flow Failure")
        send_email_notification(error_msg, "BHIV RL Flow Error")

        # Re-raise to maintain Prefect error handling
        raise


@flow
def monitored_mcp_flow(pdf_paths: list, city: str = "Mumbai"):
    """MCP flow with monitoring and notifications"""
    logger = get_run_logger()
    flow_name = "monitored_mcp_flow"

    try:
        logger.info(f"Starting {flow_name} for {city} with {len(pdf_paths)} PDFs")

        # Import and run MCP compliance
        from mcp_compliance_flow import mcp_compliance_flow

        result = mcp_compliance_flow()

        # Success notification
        success_msg = f"MCP compliance completed for {city} - {len(pdf_paths)} PDFs processed"
        logger.info(success_msg)

        return result

    except Exception as e:
        # Error notifications
        error_msg = f"MCP flow failed for {city}: {str(e)}"
        logger.error(error_msg)

        # Send alerts
        send_slack_notification(error_msg, "MCP Flow Failure")
        send_email_notification(error_msg, "BHIV MCP Flow Error")

        # Re-raise to maintain Prefect error handling
        raise


@task
def check_system_health():
    """Check system health and send alerts if needed"""
    logger = get_run_logger()

    health_issues = []

    # Check disk space
    import shutil

    disk_usage = shutil.disk_usage(".")
    free_gb = disk_usage.free / (1024**3)

    if free_gb < 1.0:  # Less than 1GB free
        health_issues.append(f"Low disk space: {free_gb:.1f}GB free")

    # Check log file sizes
    log_dir = "data/logs"
    if os.path.exists(log_dir):
        total_log_size = sum(
            os.path.getsize(os.path.join(log_dir, f))
            for f in os.listdir(log_dir)
            if os.path.isfile(os.path.join(log_dir, f))
        )

        if total_log_size > 100 * 1024 * 1024:  # More than 100MB
            health_issues.append(f"Large log files: {total_log_size / (1024*1024):.1f}MB")

    # Check for recent failures
    failure_log = "data/logs/failure_log.jsonl"
    if os.path.exists(failure_log):
        with open(failure_log, "r") as f:
            recent_failures = len(f.readlines())

        if recent_failures > 10:
            health_issues.append(f"High failure rate: {recent_failures} recent failures")

    # Send alerts if issues found
    if health_issues:
        alert_msg = "System health issues detected:\n" + "\n".join(f"- {issue}" for issue in health_issues)
        send_slack_notification(alert_msg, "System Health Alert")
        logger.warning(f"Health issues: {len(health_issues)}")
    else:
        logger.info("System health check passed")

    return {"issues": health_issues, "status": "unhealthy" if health_issues else "healthy"}


@flow
def system_health_monitoring_flow():
    """System health monitoring with notifications"""
    logger = get_run_logger()

    try:
        health_result = check_system_health()

        # Generate health report
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_status": health_result["status"],
            "issues_found": len(health_result["issues"]),
            "issues": health_result["issues"],
        }

        # Save report
        os.makedirs("data/reports", exist_ok=True)
        with open("data/reports/health_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Health monitoring completed: {health_result['status']}")
        return report

    except Exception as e:
        error_msg = f"Health monitoring failed: {str(e)}"
        logger.error(error_msg)

        send_slack_notification(error_msg, "Health Monitoring Failure")
        raise


@flow
def reliable_workflow_with_retries(workflow_name: str, max_retries: int = 3):
    """Reliable workflow with retries and notifications"""
    logger = get_run_logger()

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} for {workflow_name}")

            # Example workflow execution
            if workflow_name == "rl_optimization":
                result = monitored_rl_flow("Optimize layout", "Mumbai")
            elif workflow_name == "mcp_compliance":
                result = monitored_mcp_flow(["test.pdf"], "Mumbai")
            else:
                result = {"status": "unknown_workflow"}

            # Success - break retry loop
            success_msg = f"{workflow_name} succeeded on attempt {attempt + 1}"
            logger.info(success_msg)
            return result

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")

            if attempt == max_retries - 1:
                # Final failure - send alert
                error_msg = f"{workflow_name} failed after {max_retries} attempts: {str(e)}"
                send_slack_notification(error_msg, "Workflow Final Failure")
                send_email_notification(error_msg, "BHIV Workflow Critical Error")
                raise
            else:
                # Retry - send warning
                retry_msg = f"{workflow_name} failed on attempt {attempt + 1}, retrying..."
                logger.warning(retry_msg)

    return {"status": "max_retries_exceeded"}
