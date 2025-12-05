"""
BHIV Assistant Startup Script
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn

    # Simple config without relative imports
    host = "0.0.0.0"
    port = 8003

    print("Starting BHIV AI Assistant...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("=" * 50)

    uvicorn.run(
        "app.bhiv_assistant.app.main_bhiv:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
