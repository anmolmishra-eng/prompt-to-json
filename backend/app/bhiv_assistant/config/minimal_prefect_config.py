"""
Minimal Prefect Server Configuration for BHIV AI Assistant
Only essential endpoints for workflow orchestration
"""

import uvicorn
from fastapi import FastAPI
from prefect.server.api.server import create_app
from prefect.settings import PREFECT_API_URL, PREFECT_SERVER_API_HOST, PREFECT_SERVER_API_PORT

# Essential endpoints for BHIV system
ESSENTIAL_ENDPOINTS = {
    # Core workflow management
    "/api/flows/": ["POST", "GET"],
    "/api/flows/{id}": ["GET", "PATCH", "DELETE"],
    "/api/flows/filter": ["POST"],
    # Flow run management
    "/api/flow_runs/": ["POST"],
    "/api/flow_runs/{id}": ["GET", "PATCH"],
    "/api/flow_runs/{id}/set_state": ["POST"],
    "/api/flow_runs/filter": ["POST"],
    # Task run management
    "/api/task_runs/": ["POST"],
    "/api/task_runs/{id}": ["GET", "PATCH"],
    "/api/task_runs/{id}/set_state": ["POST"],
    "/api/task_runs/filter": ["POST"],
    # Deployment management
    "/api/deployments/": ["POST"],
    "/api/deployments/{id}": ["GET", "PATCH", "DELETE"],
    "/api/deployments/{id}/create_flow_run": ["POST"],
    "/api/deployments/filter": ["POST"],
    # Work pools and queues
    "/api/work_pools/": ["POST"],
    "/api/work_pools/{name}": ["GET", "PATCH"],
    "/api/work_pools/filter": ["POST"],
    "/api/work_pools/{work_pool_name}/queues": ["POST"],
    "/api/work_pools/{work_pool_name}/queues/{name}": ["GET"],
    # Health and monitoring
    "/api/health": ["GET"],
    "/api/version": ["GET"],
    "/api/ready": ["GET"],
    # Logs for debugging
    "/api/logs/": ["POST"],
    "/api/logs/filter": ["POST"],
}


def create_minimal_prefect_app() -> FastAPI:
    """Create minimal Prefect server with only essential endpoints"""

    # Get full Prefect app
    full_app = create_app()

    # Create new minimal app
    minimal_app = FastAPI(
        title="BHIV Prefect Server", description="Minimal Prefect server for BHIV AI Assistant", version="1.0.0"
    )

    # Copy only essential routes
    for route in full_app.routes:
        route_path = getattr(route, "path", "")
        route_methods = getattr(route, "methods", set())

        # Check if this route is essential
        is_essential = False
        for essential_path, essential_methods in ESSENTIAL_ENDPOINTS.items():
            if route_path == essential_path or route_path.startswith(essential_path.replace("{", "").replace("}", "")):
                if any(method in route_methods for method in essential_methods):
                    is_essential = True
                    break

        if is_essential:
            minimal_app.routes.append(route)

    return minimal_app


def start_minimal_prefect_server(host: str = "0.0.0.0", port: int = 4201):
    """Start minimal Prefect server"""
    print("Starting Minimal BHIV Prefect Server...")
    print(f"Essential endpoints only - {len(ESSENTIAL_ENDPOINTS)} endpoint groups")
    print(f"Server: http://{host}:{port}")

    app = create_minimal_prefect_app()

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_minimal_prefect_server()
