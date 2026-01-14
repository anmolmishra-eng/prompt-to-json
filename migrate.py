#!/usr/bin/env python3
"""Database migration script for Render deployment"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import engine, Base
from app.models import (
    User, RefreshToken, Spec, Iteration, Evaluation,
    ComplianceCheck, RLFeedback, VRRender, AuditLog,
    BHIVActivation, CityValidation, RLLiveFeedback, WorkflowRun
)

def run_migrations():
    """Create all database tables"""
    print("=" * 80)
    print("Running Database Migrations")
    print("=" * 80)

    try:
        print("\n[*] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[✓] All tables created successfully")

        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n[*] Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"    - {table}")

        print("\n" + "=" * 80)
        print("✅ Migrations Complete")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
