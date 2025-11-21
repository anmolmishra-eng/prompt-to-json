#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, ".")

import requests
from app.database import engine, get_db
from app.models import Base, RLHFFeedback, Spec
from sqlalchemy import text


def test_supabase_connection():
    """Test Supabase database connection and data"""

    print("=== SUPABASE CONNECTION TEST ===")

    # 1. Test database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"SUCCESS: Database connected: {version[:50]}...")
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return

    # 2. Test table creation
    try:
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Tables created/verified")
    except Exception as e:
        print(f"ERROR: Table creation failed: {e}")
        return

    # 3. Check existing data
    try:
        db = next(get_db())

        # Count specs
        spec_count = db.query(Spec).count()
        print(f"DATA: Specs in database: {spec_count}")

        # Count feedback
        feedback_count = db.query(RLHFFeedback).count()
        print(f"DATA: RL Feedback records: {feedback_count}")

        # Show recent specs
        recent_specs = db.query(Spec).order_by(Spec.created_at.desc()).limit(3).all()
        print(f"RECENT: Recent specs:")
        for spec in recent_specs:
            print(f"   - {spec.spec_id}: {spec.prompt[:50]}...")

        db.close()

    except Exception as e:
        print(f"ERROR: Data query failed: {e}")
        return

    # 4. Test Supabase API
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}

        response = requests.get(f"{supabase_url}/rest/v1/specs?select=count", headers=headers)
        if response.status_code == 200:
            print(f"SUCCESS: Supabase API accessible")
        else:
            print(f"ERROR: Supabase API error: {response.status_code}")

    except Exception as e:
        print(f"ERROR: Supabase API test failed: {e}")

    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    test_supabase_connection()
