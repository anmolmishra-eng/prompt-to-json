#!/usr/bin/env python3
"""
Deploy BHIV workflow to Prefect Cloud
"""

from bhiv_workflow import bhiv_workflow
from prefect import serve

if __name__ == "__main__":
    # Deploy the workflow
    bhiv_workflow.serve(
        name="bhiv-production",
        tags=["production", "ai-assistant", "bhiv"],
        parameters={"prompt": "Create a modern kitchen design", "user_id": "default"},
        interval=21600,  # Run every 6 hours (21600 seconds)
    )
