"""
Prefect Endpoint Filter for BHIV AI Assistant
Removes unnecessary endpoints to reduce server overhead
"""

from typing import Dict, List, Set


class PrefectEndpointFilter:
    """Filter to remove unnecessary Prefect endpoints"""

    # Essential endpoints for BHIV workflows
    ESSENTIAL_ENDPOINTS: Dict[str, List[str]] = {
        # Core workflow operations
        "/api/flows/": ["POST", "GET"],
        "/api/flows/{id}": ["GET", "PATCH", "DELETE"],
        "/api/flows/filter": ["POST"],
        "/api/flows/name/{name}": ["GET"],
        # Flow run operations
        "/api/flow_runs/": ["POST"],
        "/api/flow_runs/{id}": ["GET", "PATCH", "DELETE"],
        "/api/flow_runs/{id}/set_state": ["POST"],
        "/api/flow_runs/filter": ["POST"],
        "/api/flow_runs/{id}/resume": ["POST"],
        # Task run operations
        "/api/task_runs/": ["POST"],
        "/api/task_runs/{id}": ["GET", "PATCH"],
        "/api/task_runs/{id}/set_state": ["POST"],
        "/api/task_runs/filter": ["POST"],
        # Deployment operations
        "/api/deployments/": ["POST"],
        "/api/deployments/{id}": ["GET", "PATCH", "DELETE"],
        "/api/deployments/{id}/create_flow_run": ["POST"],
        "/api/deployments/filter": ["POST"],
        "/api/deployments/name/{flow_name}/{deployment_name}": ["GET"],
        # Work pool operations
        "/api/work_pools/": ["POST"],
        "/api/work_pools/{name}": ["GET", "PATCH", "DELETE"],
        "/api/work_pools/filter": ["POST"],
        "/api/work_pools/{work_pool_name}/queues": ["POST"],
        "/api/work_pools/{work_pool_name}/queues/{name}": ["GET", "PATCH", "DELETE"],
        "/api/work_pools/{work_pool_name}/workers/heartbeat": ["POST"],
        # System health
        "/api/health": ["GET"],
        "/api/version": ["GET"],
        "/api/ready": ["GET"],
        # Logging (essential for debugging)
        "/api/logs/": ["POST"],
        "/api/logs/filter": ["POST"],
    }

    # Endpoints to remove (not needed for BHIV)
    REMOVED_ENDPOINTS: Set[str] = {
        # Block management (not used)
        "/api/block_types/",
        "/api/block_documents/",
        "/api/block_schemas/",
        "/api/block_capabilities/",
        # Concurrency limits (not needed)
        "/api/concurrency_limits/",
        "/api/v2/concurrency_limits/",
        # Artifacts (not used)
        "/api/artifacts/",
        # Variables (not used)
        "/api/variables/",
        # Events (not needed)
        "/api/events",
        # Automations (not used)
        "/api/automations/",
        "/api/templates/",
        # Collections (not needed)
        "/api/collections/",
        # Admin functions (not needed in production)
        "/api/admin/",
        # UI endpoints (using custom UI)
        "/api/ui/",
        # CSRF (not needed for API-only)
        "/api/csrf-token",
        # Saved searches (not used)
        "/api/saved_searches/",
        # Task workers (using work pools)
        "/api/task_workers/",
    }

    @classmethod
    def is_endpoint_essential(cls, path: str, method: str) -> bool:
        """Check if endpoint is essential for BHIV workflows"""

        # Check exact matches
        if path in cls.ESSENTIAL_ENDPOINTS:
            return method in cls.ESSENTIAL_ENDPOINTS[path]

        # Check pattern matches (for parameterized paths)
        for essential_path, methods in cls.ESSENTIAL_ENDPOINTS.items():
            if cls._path_matches_pattern(path, essential_path):
                return method in methods

        return False

    @classmethod
    def should_remove_endpoint(cls, path: str) -> bool:
        """Check if endpoint should be removed"""

        for removed_pattern in cls.REMOVED_ENDPOINTS:
            if path.startswith(removed_pattern):
                return True

        return False

    @staticmethod
    def _path_matches_pattern(path: str, pattern: str) -> bool:
        """Check if path matches pattern with parameters"""

        # Simple pattern matching for {id}, {name} etc.
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                continue  # Parameter match
            elif pattern_part != path_part:
                return False

        return True

    @classmethod
    def get_endpoint_summary(cls) -> Dict[str, int]:
        """Get summary of endpoint filtering"""

        return {
            "essential_endpoint_groups": len(cls.ESSENTIAL_ENDPOINTS),
            "removed_endpoint_groups": len(cls.REMOVED_ENDPOINTS),
            "total_essential_methods": sum(len(methods) for methods in cls.ESSENTIAL_ENDPOINTS.values()),
        }


# Usage example
if __name__ == "__main__":
    filter_obj = PrefectEndpointFilter()
    summary = filter_obj.get_endpoint_summary()

    print("BHIV Prefect Endpoint Filter Summary:")
    print(f"✅ Essential endpoint groups: {summary['essential_endpoint_groups']}")
    print(f"❌ Removed endpoint groups: {summary['removed_endpoint_groups']}")
    print(f"🔧 Total essential methods: {summary['total_essential_methods']}")

    print("\nEssential endpoints:")
    for path, methods in PrefectEndpointFilter.ESSENTIAL_ENDPOINTS.items():
        print(f"  {path}: {', '.join(methods)}")

    print("\nRemoved endpoints:")
    for path in sorted(PrefectEndpointFilter.REMOVED_ENDPOINTS):
        print(f"  {path}*")
