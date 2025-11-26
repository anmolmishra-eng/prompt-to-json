"""
Prefect Workflows Package
Centralized workflow orchestration using Prefect Cloud
"""

from .prefect_config import get_prefect_config, setup_prefect_workspace

__all__ = ["setup_prefect_workspace", "get_prefect_config"]
