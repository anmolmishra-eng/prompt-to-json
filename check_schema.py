#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

async def check_schema():
    """Check database schema and tables"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("[OK] Connected to Supabase database")

        # List all tables
        tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        tables = await conn.fetch(tables_query)
        print(f"\nTables found: {len(tables)}")
        for table in tables:
            print(f"  - {table['table_name']}")

        # Check specs table columns if it exists
        if any(t['table_name'] == 'specs' for t in tables):
            columns_query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'specs' AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            columns = await conn.fetch(columns_query)
            print(f"\nSpecs table columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
        else:
            print("\n[INFO] No 'specs' table found")

        # Check for any table with similar name
        similar_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE '%spec%'
        ORDER BY table_name;
        """
        similar = await conn.fetch(similar_query)
        if similar:
            print(f"\nTables with 'spec' in name:")
            for table in similar:
                print(f"  - {table['table_name']}")

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_schema())
