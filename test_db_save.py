#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from datetime import datetime, timezone

async def test_db_save():
    """Test database save functionality"""
    try:
        from app.database import get_db_context
        from app.models import Spec
        import json

        print("[OK] Imports successful")

        # Test data
        spec_id = "test_spec_manual_001"
        test_spec_json = {
            "design_type": "test",
            "objects": [{"id": "test_obj", "type": "test"}],
            "metadata": {"test": True}
        }

        print(f"[TEST] Attempting to save spec {spec_id} to database...")

        with get_db_context() as db:
            # Create new spec record
            db_spec = Spec(
                id=spec_id,
                user_id="test_user_manual",
                project_id="test_project",
                prompt="Test prompt for manual save",
                city="Mumbai",
                spec_json=test_spec_json,
                design_type="test",
                preview_url="http://test.com/preview.glb",
                estimated_cost=100000.0,
                currency="INR",
                compliance_status="pending",
                status="draft",
                version=1,
                generation_time_ms=1000,
                lm_provider="test"
            )

            db.add(db_spec)
            db.commit()
            print(f"[OK] Successfully saved spec {spec_id} to database")

            # Verify it was saved
            saved_spec = db.query(Spec).filter(Spec.id == spec_id).first()
            if saved_spec:
                print(f"[OK] Verified spec exists in database: {saved_spec.id}")
                print(f"     User: {saved_spec.user_id}")
                print(f"     Type: {saved_spec.design_type}")
                print(f"     Cost: Rs.{saved_spec.estimated_cost:,.0f}")
                return True
            else:
                print(f"[ERROR] Spec not found after save")
                return False

    except Exception as e:
        print(f"[ERROR] Database save test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_save())
    if success:
        print("\n[PASS] Database save test successful")
    else:
        print("\n[FAIL] Database save test failed")
