#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg
import json
from datetime import datetime

# Database connection from .env
DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
SPEC_ID = "spec_eae7c2d28883"
USER_ID = "test_user_fixed_final"

async def verify_evaluation():
    """Verify the evaluation data is stored in Supabase database"""
    try:
        # Connect to database (disable statement cache for pgbouncer)
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("[OK] Connected to Supabase database")

        # Query the evaluations table
        query = "SELECT * FROM evaluations WHERE spec_id = $1 AND user_id = $2 ORDER BY created_at DESC LIMIT 1"
        result = await conn.fetchrow(query, SPEC_ID, USER_ID)

        if result:
            print(f"\n[OK] Evaluation found in database")
            print(f"Evaluation ID: {result['id']}")
            print(f"Spec ID: {result['spec_id']}")
            print(f"User ID: {result['user_id']}")
            print(f"Rating: {result['rating']}")
            print(f"Notes: {result['notes']}")
            print(f"Created at: {result['created_at']}")

            # Check aspects if available
            if result['aspects']:
                aspects = json.loads(result['aspects']) if isinstance(result['aspects'], str) else result['aspects']
                print(f"Aspects: {aspects}")

            # Check tags if available
            if result['tags']:
                tags = json.loads(result['tags']) if isinstance(result['tags'], str) else result['tags']
                print(f"Tags: {tags}")

            return True
        else:
            print(f"[ERROR] Evaluation not found for spec {SPEC_ID} and user {USER_ID}")

            # Check all evaluations
            all_evals = await conn.fetch("SELECT id, spec_id, user_id, rating, created_at FROM evaluations ORDER BY created_at DESC LIMIT 5")
            print(f"\nRecent evaluations in database ({len(all_evals)} found):")
            for eval_row in all_evals:
                print(f"  - ID: {eval_row['id']}, Spec: {eval_row['spec_id']}, User: {eval_row['user_id']}, Rating: {eval_row['rating']}")

            return False

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def verify_spec_exists():
    """Verify the spec still exists"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)

        query = "SELECT id, user_id, design_type FROM specs WHERE id = $1"
        result = await conn.fetchrow(query, SPEC_ID)

        if result:
            print(f"[OK] Spec exists: {result['id']} (type: {result['design_type']}, user: {result['user_id']})")
            return True
        else:
            print(f"[ERROR] Spec not found: {SPEC_ID}")
            return False

    except Exception as e:
        print(f"[ERROR] Spec check failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def main():
    print("Verifying evaluation data in Supabase database...")
    print("=" * 60)

    # First verify the spec exists
    spec_exists = await verify_spec_exists()

    if spec_exists:
        # Then verify the evaluation
        eval_success = await verify_evaluation()

        print("\n" + "=" * 60)
        if eval_success:
            print("[PASS] EVALUATION VERIFICATION: PASSED")
            print("Evaluation data is correctly stored in Supabase!")
        else:
            print("[FAIL] EVALUATION VERIFICATION: FAILED")
    else:
        print("\n[ERROR] Cannot verify evaluation - spec doesn't exist")

if __name__ == "__main__":
    asyncio.run(main())
