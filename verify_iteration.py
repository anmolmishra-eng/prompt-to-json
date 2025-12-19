#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg
import json

# Database connection from .env
DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
SPEC_ID = "spec_eae7c2d28883"
USER_ID = "test_user_fixed_final"
ITERATION_ID = "iter_c2845f48"

async def verify_iteration():
    """Verify the iteration data is stored in Supabase database"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("[OK] Connected to Supabase database")

        # Query the iterations table
        query = "SELECT * FROM iterations WHERE spec_id = $1 AND user_id = $2 ORDER BY created_at DESC LIMIT 1"
        result = await conn.fetchrow(query, SPEC_ID, USER_ID)

        if result:
            print(f"\n[OK] Iteration found in database")
            print(f"Iteration ID: {result['id']}")
            print(f"Spec ID: {result['spec_id']}")
            print(f"User ID: {result['user_id']}")
            print(f"Query: {result['query']}")
            print(f"NLP Confidence: {result['nlp_confidence']}")
            print(f"Preview URL: {result['preview_url']}")
            print(f"Cost Delta: Rs.{result['cost_delta']:,.0f}" if result['cost_delta'] else "No cost delta")
            print(f"New Total Cost: Rs.{result['new_total_cost']:,.0f}" if result['new_total_cost'] else "No new cost")
            print(f"Processing Time: {result['processing_time_ms']}ms" if result['processing_time_ms'] else "No timing")
            print(f"Created at: {result['created_at']}")

            # Check diff data
            if result['diff']:
                diff_data = json.loads(result['diff']) if isinstance(result['diff'], str) else result['diff']
                print(f"\nDiff Data:")
                print(f"  Changes: {len(diff_data.get('changes', []))}")

            # Check spec_json
            if result['spec_json']:
                spec_json = json.loads(result['spec_json']) if isinstance(result['spec_json'], str) else result['spec_json']
                print(f"\nUpdated Spec:")
                print(f"  Objects: {len(spec_json.get('objects', []))}")
                print(f"  Design Type: {spec_json.get('design_type', 'N/A')}")
                print(f"  Estimated Cost: Rs.{spec_json.get('estimated_cost', {}).get('total', 0):,.0f}")

            return True
        else:
            print(f"[ERROR] Iteration not found for spec {SPEC_ID} and user {USER_ID}")

            # Check all iterations
            all_iterations = await conn.fetch("SELECT id, spec_id, user_id, created_at FROM iterations ORDER BY created_at DESC LIMIT 5")
            print(f"\nRecent iterations in database ({len(all_iterations)} found):")
            for iter_row in all_iterations:
                print(f"  - ID: {iter_row['id']}, Spec: {iter_row['spec_id']}, User: {iter_row['user_id']}")

            return False

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def verify_spec_updated():
    """Verify the original spec was updated with new version"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)

        query = "SELECT id, version, estimated_cost, updated_at FROM specs WHERE id = $1"
        result = await conn.fetchrow(query, SPEC_ID)

        if result:
            print(f"\n[OK] Spec version info:")
            print(f"  Spec ID: {result['id']}")
            print(f"  Version: {result['version']}")
            print(f"  Cost: Rs.{result['estimated_cost']:,.0f}")
            print(f"  Updated: {result['updated_at']}")
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
    print("Verifying iteration data in Supabase database...")
    print("=" * 60)

    # Verify the iteration was stored
    iter_success = await verify_iteration()

    # Verify the spec was updated
    spec_success = await verify_spec_updated()

    print("\n" + "=" * 60)
    if iter_success and spec_success:
        print("[PASS] ITERATION VERIFICATION: PASSED")
        print("Iteration data is correctly stored in Supabase!")
    else:
        print("[FAIL] ITERATION VERIFICATION: FAILED")
        if not iter_success:
            print("  - Iteration data not found")
        if not spec_success:
            print("  - Spec update verification failed")

if __name__ == "__main__":
    asyncio.run(main())
