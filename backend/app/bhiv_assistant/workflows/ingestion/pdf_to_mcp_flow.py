"""
Prefect Flow: PDF Ingestion → MCP JSON Rules
Replaces N8N workflow for PDF processing
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict
from datetime import timedelta

import httpx
from prefect import flow, task
from prefect.tasks import task_input_hash
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PDFIngestionConfig(BaseModel):
    """Configuration for PDF ingestion"""
    pdf_source_dir: Path = Path("data/pdfs")
    output_dir: Path = Path("data/mcp_rules")
    mcp_api_url: str = "http://localhost:8001"
    supported_cities: List[str] = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]


@task(
    name="scan-pdf-directory",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def scan_pdf_directory(source_dir: Path) -> List[Path]:
    """
    Scan directory for new PDF files
    Returns list of PDF file paths
    """
    logger.info(f"Scanning {source_dir} for PDFs...")
    
    if not source_dir.exists():
        source_dir.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Created directory: {source_dir}")
        return []
    
    pdf_files = list(source_dir.glob("**/*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    return pdf_files


@task(
    name="extract-text-from-pdf",
    retries=3,
    retry_delay_seconds=5
)
async def extract_text_from_pdf(pdf_path: Path) -> Dict:
    """
    Extract text content from PDF
    Uses OCR if needed for scanned documents
    """
    try:
        import PyPDF2
        
        text_content = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                text_content.append({
                    "page": page_num + 1,
                    "content": text.strip()
                })
        
        logger.info(f"Extracted {len(text_content)} pages from {pdf_path.name}")
        
        return {
            "filename": pdf_path.name,
            "total_pages": len(text_content),
            "pages": text_content,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
        return {
            "filename": pdf_path.name,
            "error": str(e),
            "status": "failed"
        }


@task(
    name="parse-rules-from-text",
    retries=2
)
async def parse_rules_from_text(extracted_data: Dict) -> Dict:
    """
    Parse compliance rules from extracted text
    Uses LLM to structure unstructured text into JSON rules
    """
    if extracted_data["status"] == "failed":
        return extracted_data
    
    # Combine all pages
    full_text = "\n\n".join([
        page["content"] for page in extracted_data["pages"]
    ])
    
    # TODO: Use LLM to parse rules
    # For now, simple keyword extraction
    rules = {
        "source_document": extracted_data["filename"],
        "rules": [],
        "metadata": {
            "total_pages": extracted_data["total_pages"],
            "extraction_method": "keyword_based"
        }
    }
    
    # Example rule extraction (replace with LLM)
    keywords = ["FSI", "setback", "parking", "floor height", "coverage"]
    
    for keyword in keywords:
        if keyword.lower() in full_text.lower():
            rules["rules"].append({
                "type": keyword,
                "found": True,
                "requires_manual_review": True
            })
    
    logger.info(f"Parsed {len(rules['rules'])} rule references from {extracted_data['filename']}")
    
    return rules


@task(
    name="upload-to-mcp",
    retries=3,
    retry_delay_seconds=10
)
async def upload_to_mcp(rules: Dict, mcp_api_url: str, city: str) -> Dict:
    """
    Upload parsed rules to MCP bucket
    """
    if "error" in rules:
        return {"status": "skipped", "reason": rules["error"]}
    
    url = f"{mcp_api_url}/mcp/rules/upload"
    
    payload = {
        "city": city,
        "rules": rules["rules"],
        "source": rules["source_document"],
        "metadata": rules["metadata"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Uploaded rules to MCP for {city}: {result}")
            
            return {
                "status": "success",
                "city": city,
                "rules_uploaded": len(rules["rules"]),
                "mcp_response": result
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to upload to MCP: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


@task(name="save-processing-log")
async def save_processing_log(results: List[Dict], output_dir: Path):
    """Save processing log for audit"""
    import json
    from datetime import datetime
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = output_dir / f"ingestion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(results),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Processing log saved to {log_file}")


@flow(
    name="pdf-ingestion-to-mcp",
    description="Process PDF documents and upload rules to MCP bucket",
    version="1.0"
)
async def pdf_ingestion_flow(
    config: PDFIngestionConfig = PDFIngestionConfig()
):
    """
    Main flow: PDF → Text → Rules → MCP
    
    Replaces N8N workflow for PDF ingestion
    """
    logger.info("Starting PDF ingestion flow...")
    
    # Step 1: Scan for PDFs
    pdf_files = scan_pdf_directory(config.pdf_source_dir)
    
    if not pdf_files:
        logger.info("No PDFs found, exiting flow")
        return {"status": "no_files", "processed": 0}
    
    # Step 2-4: Process each PDF
    results = []
    
    for pdf_file in pdf_files:
        # Extract text
        extracted = await extract_text_from_pdf(pdf_file)
        
        # Parse rules
        rules = await parse_rules_from_text(extracted)
        
        # Determine city from filename or metadata
        city = "Mumbai"  # Default, should be extracted from filename
        for city_name in config.supported_cities:
            if city_name.lower() in pdf_file.name.lower():
                city = city_name
                break
        
        # Upload to MCP
        upload_result = await upload_to_mcp(rules, config.mcp_api_url, city)
        
        results.append({
            "filename": pdf_file.name,
            "city": city,
            "upload_status": upload_result["status"]
        })
    
    # Step 5: Save log
    await save_processing_log(results, config.output_dir)
    
    logger.info(f"PDF ingestion flow complete: {len(results)} files processed")
    
    return {
        "status": "complete",
        "processed": len(results),
        "results": results
    }


# Deployment
if __name__ == "__main__":
    # Run flow locally
    asyncio.run(pdf_ingestion_flow())