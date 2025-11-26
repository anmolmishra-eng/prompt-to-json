"""
Test PDF Ingestion Workflow
"""

import asyncio
import tempfile
from pathlib import Path

from .pdf_to_mcp_flow import PDFIngestionConfig, pdf_ingestion_flow


async def test_pdf_workflow():
    """Test the PDF ingestion workflow"""
    print("Testing PDF Ingestion Workflow...")

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pdf_dir = temp_path / "pdfs"
        output_dir = temp_path / "output"

        pdf_dir.mkdir()
        output_dir.mkdir()

        # Create test configuration
        config = PDFIngestionConfig(pdf_source_dir=pdf_dir, output_dir=output_dir, mcp_api_url="http://localhost:8001")

        print(f"Test directories:")
        print(f"  PDF source: {pdf_dir}")
        print(f"  Output: {output_dir}")

        # Create a dummy PDF file for testing
        dummy_pdf = pdf_dir / "mumbai_dcr_test.pdf"
        dummy_pdf.write_text("Dummy PDF content for testing")

        print(f"Created test file: {dummy_pdf}")

        try:
            # Run the workflow
            result = await pdf_ingestion_flow(config)

            print("\nWorkflow Result:")
            print(f"  Status: {result['status']}")
            print(f"  Files processed: {result['processed']}")

            if result.get("results"):
                for file_result in result["results"]:
                    print(f"  - {file_result['filename']}: {file_result['upload_status']}")

            return result

        except Exception as e:
            print(f"Workflow failed: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(test_pdf_workflow())
    print(f"\nTest completed with status: {result.get('status')}")
