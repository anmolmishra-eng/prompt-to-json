#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio

async def check_users():
    """Check what users exist in database"""
    try:
        from app.database import get_db_context
        from app.models import User

        print("[OK] Checking users in database...")

        with get_db_context() as db:
            users = db.query(User).all()

            print(f"\nUsers found: {len(users)}")
            for user in users:
                print(f"  - ID: {user.id}")
                print(f"    Username: {user.username}")
                print(f"    Email: {user.email}")
                print(f"    Active: {user.is_active}")
                print(f"    Created: {user.created_at}")
                print("-" * 40)

            return users

    except Exception as e:
        print(f"[ERROR] Failed to check users: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    users = asyncio.run(check_users())
