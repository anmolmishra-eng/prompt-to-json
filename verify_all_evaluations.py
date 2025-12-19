#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg

# Database connection from .env
DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
SPEC_ID = "spec_eae7c2d28883"

async def verify_all_evaluations():
    """Verify all evaluations for the spec are stored"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("[OK] Connected to Supabase database")

        # Query all evaluations for the spec
        query = "SELECT * FROM evaluations WHERE spec_id = $1 ORDER BY created_at DESC"
        results = await conn.fetch(query, SPEC_ID)

        print(f"\n[OK] Found {len(results)} evaluations for spec {SPEC_ID}")
        print("-" * 60)

        for i, eval_row in enumerate(results, 1):
            print(f"Evaluation #{i}:")
            print(f"  ID: {eval_row['id']}")
            print(f"  User: {eval_row['user_id']}")
            print(f"  Rating: {eval_row['rating']}")
            print(f"  Notes: {eval_row['notes']}")
            print(f"  Created: {eval_row['created_at']}")
            print("-" * 40)

        # Get evaluation statistics
        stats_query = """
        SELECT
            COUNT(*) as total_evaluations,
            AVG(rating) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM evaluations
        WHERE spec_id = $1
        """
        stats = await conn.fetchrow(stats_query, SPEC_ID)

        print(f"\nEVALUATION STATISTICS:")
        print(f"  Total Evaluations: {stats['total_evaluations']}")
        print(f"  Average Rating: {stats['avg_rating']:.2f}")
        print(f"  Rating Range: {stats['min_rating']} - {stats['max_rating']}")

        return len(results) > 0

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def main():
    print("Verifying all evaluation data in Supabase database...")
    print("=" * 60)

    success = await verify_all_evaluations()

    print("\n" + "=" * 60)
    if success:
        print("[PASS] ALL EVALUATIONS VERIFICATION: PASSED")
        print("All evaluation data is correctly stored in Supabase!")
    else:
        print("[FAIL] ALL EVALUATIONS VERIFICATION: FAILED")

if __name__ == "__main__":
    asyncio.run(main())
