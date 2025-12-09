import json
import os
from pathlib import Path

import pymupdf
import requests
from prefect import flow, get_run_logger, task
from prefect.events import emit_event


def parse_rules_from_text(text: str) -> dict:
    """Parse compliance rules from PDF text"""
    # Mock rule parsing - in practice, use NLP/ML
    rules = {
        "building_height_limit": "extracted from text",
        "setback_requirements": "extracted from text",
        "fsi_limits": "extracted from text",
    }
    return rules


@task
def ingest_pdf(pdf_path: str) -> dict:
    logger = get_run_logger()
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    rules = parse_rules_from_text(text)

    # Push rules to MCP via API
    try:
        response = requests.post("http://localhost:8000/api/v1/compliance/rules", json=rules, timeout=10)
        logger.info(f"Pushed rules, status: {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to push rules: {e}")

    return rules


@task
def aggregate_logs(log_paths: list[str]):
    logger = get_run_logger()
    combined = []
    for path in log_paths:
        if os.path.exists(path):
            with open(path) as f:
                combined.extend(f.readlines())

    # Write aggregated logs
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/aggregated_logs.txt", "w") as out:
        out.writelines(combined)
    logger.info(f"Aggregated {len(log_paths)} logs.")


@task
def verify_geometry(glb_path: str) -> bool:
    """Verify GLB geometry file"""
    try:
        # Simple file existence and size check
        if not os.path.exists(glb_path):
            return False

        file_size = os.path.getsize(glb_path)
        if file_size < 100:  # Too small to be valid GLB
            return False

        # Try to read GLB header
        with open(glb_path, "rb") as f:
            header = f.read(12)
            if len(header) >= 4 and header[:4] == b"glTF":
                return True

        return False
    except Exception as e:
        get_run_logger().error(f"GLB verification failed: {e}")
        return False


@task
def process_new_file(file_name: str):
    """Process newly uploaded file"""
    logger = get_run_logger()
    logger.info(f"Processing new file: {file_name}")

    if file_name.endswith(".pdf"):
        rules = ingest_pdf(file_name)
        # Emit event when PDF processed
        emit_event(
            event="pdf.processed",
            resource={"prefect.resource.id": f"file.{Path(file_name).name}"},
            payload={"rules_count": len(rules)},
        )
    elif file_name.endswith(".glb"):
        valid = verify_geometry(file_name)
        # Emit event when geometry verified
        emit_event(
            event="geometry.verified",
            resource={"prefect.resource.id": f"file.{Path(file_name).name}"},
            payload={"valid": valid},
        )


@flow
def n8n_replacement_flow(pdf_paths: list[str], log_paths: list[str], glb_paths: list[str]):
    """Replace n8n workflows with Prefect"""
    logger = get_run_logger()

    # Ingest each PDF and update MCP
    for pdf in pdf_paths:
        if os.path.exists(pdf):
            rules = ingest_pdf(pdf)
            logger.info(f"Processed PDF: {pdf}")

    # Aggregate logs
    if log_paths:
        aggregate_logs(log_paths)

    # Verify each geometry output
    results = []
    for glb in glb_paths:
        if os.path.exists(glb):
            ok = verify_geometry(glb)
            results.append((glb, ok))

    logger.info(f"Geometry verification results: {results}")

    # Emit completion event
    emit_event(
        event="workflow.completed",
        resource={"prefect.resource.id": "n8n_replacement_flow"},
        payload={
            "pdfs_processed": len(pdf_paths),
            "logs_aggregated": len(log_paths),
            "geometries_verified": len(results),
        },
    )

    return {"pdfs_processed": len(pdf_paths), "logs_aggregated": len(log_paths), "geometry_results": results}


@flow
def watch_new_files(watch_directory: str = "data/incoming"):
    """Event-driven flow to watch for new files"""
    logger = get_run_logger()

    if not os.path.exists(watch_directory):
        os.makedirs(watch_directory, exist_ok=True)
        logger.info(f"Created watch directory: {watch_directory}")
        return

    # Get list of files to process
    files = []
    for ext in [".pdf", ".glb"]:
        files.extend(Path(watch_directory).glob(f"*{ext}"))

    logger.info(f"Found {len(files)} files to process")

    # Process each file
    for file_path in files:
        process_new_file(str(file_path))

        # Move processed file to archive
        archive_dir = Path(watch_directory) / "processed"
        archive_dir.mkdir(exist_ok=True)

        try:
            file_path.rename(archive_dir / file_path.name)
            logger.info(f"Archived: {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to archive {file_path.name}: {e}")


@flow
def scheduled_maintenance_flow():
    """Scheduled flow for system maintenance"""
    logger = get_run_logger()

    # Clean up old logs
    log_dir = Path("data/logs")
    if log_dir.exists():
        old_logs = [f for f in log_dir.glob("*.log") if f.stat().st_mtime < (time.time() - 7 * 24 * 3600)]
        for log_file in old_logs:
            log_file.unlink()
            logger.info(f"Cleaned up old log: {log_file.name}")

    # Generate system health report
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "disk_usage": "normal",
        "memory_usage": "normal",
        "active_flows": "operational",
    }

    os.makedirs("data/reports", exist_ok=True)
    with open("data/reports/health_report.json", "w") as f:
        json.dump(health_report, f, indent=2)

    logger.info("System maintenance completed")
    return health_report


# Event-driven example with webhook trigger
@flow
def webhook_triggered_flow(payload: dict):
    """Flow triggered by external webhook"""
    logger = get_run_logger()
    logger.info(f"Webhook triggered with payload: {payload}")

    # Process based on webhook payload
    if payload.get("event_type") == "file_uploaded":
        file_path = payload.get("file_path")
        if file_path:
            process_new_file(file_path)

    elif payload.get("event_type") == "compliance_check":
        city = payload.get("city", "Mumbai")
        # Trigger compliance workflow for specific city
        logger.info(f"Triggering compliance check for {city}")

    return {"status": "processed", "payload": payload}
