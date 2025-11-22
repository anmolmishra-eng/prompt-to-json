"""
BHIV Assistant Startup Script
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from config.integration_config import IntegrationConfig

    config = IntegrationConfig()

    print("Starting BHIV AI Assistant...")
    print(f"Host: {config.bhiv.api_host}")
    print(f"Port: {config.bhiv.api_port}")
    print("=" * 50)

    uvicorn.run(
        "app.main_bhiv:app",
        host=config.bhiv.api_host,
        port=config.bhiv.api_port,
        reload=True,
        log_level=config.bhiv.log_level.lower(),
    )
