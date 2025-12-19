#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import json

# The spec_id from the generate response
SPEC_ID = "spec_eae7c2d28883"
USER_ID = "test_user_fixed_final"

async def verify_complete_storage():
    """Verify spec is stored in both database and memory"""
    print("=" * 60)
    print("COMPREHENSIVE STORAGE VERIFICATION")
    print("=" * 60)

    database_success = False
    memory_success = False

    # 1. Check Database Storage
    print("\n1. CHECKING DATABASE STORAGE (Supabase)")
    print("-" * 40)

    try:
        from app.database import get_db_context
        from app.models import Spec, User

        with get_db_context() as db:
            # Check if spec exists in database
            db_spec = db.query(Spec).filter(Spec.id == SPEC_ID).first()

            if db_spec:
                print(f"[OK] Spec found in database: {SPEC_ID}")
                print(f"     User ID: {db_spec.user_id}")
                print(f"     Design Type: {db_spec.design_type}")
                print(f"     Cost: Rs.{db_spec.estimated_cost:,.0f}")
                print(f"     Status: {db_spec.status}")
                print(f"     Version: {db_spec.version}")
                print(f"     Created: {db_spec.created_at}")
                print(f"     Preview URL: {db_spec.preview_url}")

                # Verify spec_json structure
                spec_json = db_spec.spec_json
                if isinstance(spec_json, str):
                    spec_json = json.loads(spec_json)

                print(f"     Objects: {len(spec_json.get('objects', []))}")
                print(f"     Dimensions: {spec_json.get('dimensions', {})}")

                database_success = True
            else:
                print(f"[ERROR] Spec not found in database: {SPEC_ID}")

                # Check recent specs
                recent_specs = db.query(Spec).order_by(Spec.created_at.desc()).limit(5).all()
                print(f"\nRecent specs in database ({len(recent_specs)} found):")
                for spec in recent_specs:
                    print(f"  - {spec.id} (user: {spec.user_id}, created: {spec.created_at})")

            # Check if user was created
            user = db.query(User).filter(User.id == USER_ID).first()
            if user:
                print(f"[OK] User found in database: {user.username}")
            else:
                print(f"[ERROR] User not found in database: {USER_ID}")

    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        import traceback
        traceback.print_exc()

    # 2. Check Memory Storage
    print("\n2. CHECKING MEMORY STORAGE")
    print("-" * 40)

    try:
        from app.spec_storage import get_spec, get_all_specs

        # Check if spec exists in memory
        memory_spec = get_spec(SPEC_ID)

        if memory_spec:
            print(f"[OK] Spec found in memory: {SPEC_ID}")
            print(f"     User ID: {memory_spec['user_id']}")
            print(f"     Cost: Rs.{memory_spec['estimated_cost']:,.0f}")
            print(f"     Version: {memory_spec['spec_version']}")
            print(f"     Created: {memory_spec['created_at']}")

            spec_json = memory_spec['spec_json']
            print(f"     Objects: {len(spec_json.get('objects', []))}")

            memory_success = True
        else:
            print(f"[ERROR] Spec not found in memory: {SPEC_ID}")

            # Check all specs in memory
            all_specs = get_all_specs()
            print(f"\nAll specs in memory ({len(all_specs)} found):")
            for spec_id in all_specs.keys():
                print(f"  - {spec_id}")

    except Exception as e:
        print(f"[ERROR] Memory check failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Test API Retrieval
    print("\n3. TESTING API RETRIEVAL")
    print("-" * 40)

    api_success = False
    try:
        import httpx

        # Get fresh token
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                data={"username": "admin", "password": "bhiv2024"}
            )

            if login_response.status_code == 200:
                token = login_response.json()["access_token"]

                # Test GET endpoint
                get_response = await client.get(
                    f"http://localhost:8000/api/v1/specs/{SPEC_ID}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if get_response.status_code == 200:
                    api_data = get_response.json()
                    print(f"[OK] API retrieval successful")
                    print(f"     Spec ID: {api_data['spec_id']}")
                    print(f"     User ID: {api_data['user_id']}")
                    print(f"     Cost: Rs.{api_data['estimated_cost']:,.0f}")
                    print(f"     Objects: {len(api_data['spec_json'].get('objects', []))}")

                    api_success = True
                else:
                    print(f"[ERROR] API retrieval failed: {get_response.status_code}")
                    print(f"Response: {get_response.text}")
            else:
                print(f"[ERROR] Authentication failed: {login_response.status_code}")

    except Exception as e:
        print(f"[ERROR] API test failed: {e}")

    # 4. Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    print(f"Database Storage: {'PASS' if database_success else 'FAIL'}")
    print(f"Memory Storage:   {'PASS' if memory_success else 'FAIL'}")
    print(f"API Retrieval:    {'PASS' if api_success else 'FAIL'}")

    overall_success = database_success and memory_success and api_success
    print(f"\nOverall Status:   {'PASS' if overall_success else 'FAIL'}")

    if overall_success:
        print("\n✅ All storage mechanisms are working correctly!")
        print("   - Spec is saved to Supabase database")
        print("   - Spec is cached in memory storage")
        print("   - API can retrieve spec from both sources")
    else:
        print("\n❌ Some storage mechanisms are failing:")
        if not database_success:
            print("   - Database storage is not working")
        if not memory_success:
            print("   - Memory storage is not working")
        if not api_success:
            print("   - API retrieval is not working")

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(verify_complete_storage())
