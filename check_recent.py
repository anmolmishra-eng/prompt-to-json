#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg
import json

DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

async def check_recent():
    """Check recent specs in database"""
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("[OK] Connected to Supabase database")

        # Get all recent specs
        query = """
        SELECT id, user_id, created_at, design_type, estimated_cost, status
        FROM specs
        ORDER BY created_at DESC
        LIMIT 10
        """
        results = await conn.fetch(query)

        print(f"\nRecent specs in database ({len(results)} found):")
        print("-" * 80)
        for spec in results:
            print(f"ID: {spec['id']}")
            print(f"User: {spec['user_id']}")
            print(f"Type: {spec['design_type']}")
            print(f"Cost: Rs.{spec['estimated_cost']:,.0f}" if spec['estimated_cost'] else "No cost")
            print(f"Status: {spec['status']}")
            print(f"Created: {spec['created_at']}")
            print("-" * 40)

        # Check if our specific spec exists with any variation
        search_query = """
        SELECT id, user_id, created_at
        FROM specs
        WHERE id LIKE '%a737ef45eeb9%' OR user_id = 'test_user_456'
        ORDER BY created_at DESC
        """
        search_results = await conn.fetch(search_query)

        if search_results:
            print(f"\nFound matching specs:")
            for spec in search_results:
                print(f"  - {spec['id']} (user: {spec['user_id']}, created: {spec['created_at']})")
        else:
            print(f"\nNo specs found matching 'a737ef45eeb9' or user 'test_user_456'")

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_recent())
