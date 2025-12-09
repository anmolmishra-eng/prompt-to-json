import glob
import json
import os

import pdfplumber
from prefect import flow, get_run_logger, task


@task
def ingest_pdf(file_path: str) -> dict:
    """Read a PDF file and extract text/data (e.g. using pdfplumber or PyMuPDF)."""
    data = {}
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        data["text"] = text
    logger = get_run_logger()
    logger.info(f"Ingested PDF {file_path}")
    return data


@task
def apply_mcp_rules(pdf_data: dict) -> dict:
    """Call the multi-agent compliance (MCP) system to process extracted data."""
    rules_input = pdf_data.get("text", "")
    # For illustration, pretend we parse rules into JSON:
    compliance_result = {"compliant": True, "issues": []}
    # ... insert actual compliance logic here ...
    logger = get_run_logger()
    logger.info(f"Applied MCP rules, compliance result: {compliance_result}")
    return compliance_result


@task
def save_json(data: dict, output_path: str):
    """Save the given data dict as JSON to the specified path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    logger = get_run_logger()
    logger.info(f"Saved output JSON to {output_path}")


@flow(name="MCP_Compliance_Workflow")
def mcp_compliance_flow(input_dir: str = "data/incoming_pdfs", output_dir: str = "data/compliance_output"):
    """
    Prefect flow that replaces the n8n PDF ingestion → MCP workflow.
    Scans for PDFs, processes each, and saves JSON outputs.
    """
    pdf_paths = glob.glob(os.path.join(input_dir, "*.pdf"))
    for pdf_path in pdf_paths:
        data = ingest_pdf(pdf_path)
        result = apply_mcp_rules(data)
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        save_json(result, f"{output_dir}/{base}_compliance.json")


@task
def aggregate_logs(log_dir: str) -> dict:
    """Aggregate logs from multiple runs into a single summary."""
    combined = {"entries": []}
    for log_file in glob.glob(f"{log_dir}/*.json"):
        with open(log_file) as f:
            log = json.load(f)
            combined["entries"].append(log)
    return combined


@task
def verify_geometry(output_glb: str) -> bool:
    """Verify a .glb geometry file (placeholder logic)."""
    exists = os.path.exists(output_glb)
    # Here one could add actual GLB validation, 3D checks, etc.
    return exists


@flow(name="Log_Aggregation_Workflow")
def log_aggregation_flow(log_dir: str = "data/logs", summary_path: str = "data/logs/summary.json"):
    summary = aggregate_logs(log_dir)
    save_json(summary, summary_path)


@flow(name="Geometry_Verification_Workflow")
def geometry_verification_flow(geometry_dir: str = "data/geometry"):
    all_valid = True
    for glb_file in glob.glob(f"{geometry_dir}/*.glb"):
        valid = verify_geometry(glb_file)
        if not valid:
            get_run_logger().warning(f"Geometry file failed verification: {glb_file}")
            all_valid = False
    return all_valid
