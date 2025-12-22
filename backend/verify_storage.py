#!/usr/bin/env python3
"""
Verify BHIV endpoint data storage in database
"""
from app.database import get_db
from app.models import Spec, WorkflowRun
from sqlalchemy.orm import Session


def verify_database_storage():
    """Check if BHIV request was stored in database"""
    db = next(get_db())

    # Check latest spec for test user
    latest_spec = db.query(Spec).filter(Spec.user_id == "test_user_123").order_by(Spec.created_at.desc()).first()

    if latest_spec:
        print(f"SPEC FOUND:")
        print(f"  ID: {latest_spec.id}")
        print(f"  Prompt: {latest_spec.prompt}")
        print(f"  City: {latest_spec.city}")
        print(f"  Design Type: {latest_spec.design_type}")
        print(f"  Status: {latest_spec.status}")
        print(f"  Cost: {latest_spec.estimated_cost} {latest_spec.currency}")
        print(f"  Created: {latest_spec.created_at}")
        print(f"  Spec JSON Keys: {list(latest_spec.spec_json.keys()) if latest_spec.spec_json else 'None'}")
    else:
        print("NO SPEC FOUND for test_user_123")

    # Check workflow runs
    workflow_runs = db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).limit(3).all()

    print(f"\nWORKFLOW RUNS ({len(workflow_runs)} found):")
    for run in workflow_runs:
        print(f"  Flow: {run.flow_name}")
        print(f"  Status: {run.status}")
        print(f"  Created: {run.created_at}")
        print(f"  Parameters: {run.parameters}")
        print("  ---")

    db.close()


if __name__ == "__main__":
    verify_database_storage()
