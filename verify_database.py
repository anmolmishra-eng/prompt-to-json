#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg
import json
from datetime import datetime

# Database connection from .env
DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
SPEC_ID = "spec_eae7c2d28883"

async def verify_database():
    """Verify the spec data is stored in Supabase database"""
    try:
        # Connect to database (disable statement cache for pgbouncer)
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("[OK] Connected to Supabase database")

        # Query the specs table
        query = "SELECT * FROM specs WHERE id = $1"
        result = await conn.fetchrow(query, SPEC_ID)

        if result:
            print(f"\n[OK] Spec found in database: {SPEC_ID}")
            print(f"Created at: {result['created_at']}")
            print(f"User ID: {result['user_id']}")
            print(f"Estimated cost: Rs.{result['estimated_cost']:,.0f}")
            print(f"Version: {result['version']}")
            print(f"Preview URL: {result['preview_url']}")
            print(f"Status: {result['status']}")
            print(f"City: {result['city']}")

            # Parse and display spec_json
            spec_json = json.loads(result['spec_json']) if isinstance(result['spec_json'], str) else result['spec_json']
            print(f"\nDesign Details:")
            print(f"   Type: {spec_json.get('design_type', 'N/A')}")
            print(f"   Style: {spec_json.get('style', 'N/A')}")
            print(f"   Objects: {len(spec_json.get('objects', []))}")

            return True
        else:
            print(f"[ERROR] Spec not found in database: {SPEC_ID}")
            # Let's check what specs exist
            all_specs = await conn.fetch("SELECT id, created_at FROM specs ORDER BY created_at DESC LIMIT 5")
            print(f"Recent specs in database:")
            for spec in all_specs:
                print(f"  - {spec['id']} (created: {spec['created_at']})")
            return False

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def main():
    print("Verifying spec data in Supabase database...")
    print("=" * 50)

    success = await verify_database()

    print("\n" + "=" * 50)
    if success:
        print("[PASS] DATABASE VERIFICATION: PASSED")
        print("Data is correctly stored in Supabase!")
    else:
        print("[FAIL] DATABASE VERIFICATION: FAILED")

if __name__ == "__main__":
    asyncio.run(main())
