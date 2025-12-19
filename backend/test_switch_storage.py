#!/usr/bin/env python3
"""
Test switch endpoint storage verification
"""
import os
import sys

sys.path.append(".")

import json

from app.spec_storage import get_spec, list_specs


def test_switch_storage():
    """Test if switch endpoint stored data correctly"""
    print("Testing Switch Storage")
    print("=" * 40)

    # 1. Check in-memory storage
    stored_specs = list_specs()
    print(f"Specs in memory storage: {len(stored_specs)}")

    for spec_id, spec_data in stored_specs.items():
        print(f"\nSpec ID: {spec_id}")
        print(f"Version: {spec_data.get('spec_version', 1)}")
        print(f"User ID: {spec_data.get('user_id', 'N/A')}")

        # Check objects and their colors
        objects = spec_data.get("spec_json", {}).get("objects", [])
        print(f"Objects: {len(objects)}")

        for obj in objects:
            print(f"  {obj['id']}: {obj['type']} - color: {obj.get('color_hex', 'N/A')}")

        print(f"Estimated cost: {spec_data.get('spec_json', {}).get('estimated_cost', {}).get('total', 'N/A')}")
        print("-" * 50)

    # 2. Test specific spec retrieval
    test_spec_id = "spec_2810cc7fe9b6"
    spec = get_spec(test_spec_id)

    if spec:
        print(f"\nRetrieved spec {test_spec_id}:")
        print(f"Version: {spec.get('spec_version', 1)}")

        # Check if colors were actually changed
        objects = spec.get("spec_json", {}).get("objects", [])
        red_count = sum(1 for obj in objects if obj.get("color_hex") == "#FF0000")
        green_count = sum(1 for obj in objects if obj.get("color_hex") == "#00FF00")

        print(f"Objects with red color (#FF0000): {red_count}")
        print(f"Objects with green color (#00FF00): {green_count}")

        if green_count > 0:
            print("✅ Switch operations successfully applied!")
        else:
            print("❌ Switch operations not found")
    else:
        print(f"❌ Spec {test_spec_id} not found in memory storage")

    # 3. Check for any local files
    local_dirs = ["data/switches", "data/iterations", "data/specs"]
    for dir_path in local_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"\nFiles in {dir_path}: {len(files)}")
            for file in files[:3]:
                print(f"  {file}")
        else:
            print(f"\nDirectory {dir_path} does not exist")

    return True


if __name__ == "__main__":
    success = test_switch_storage()
    if success:
        print("\n✅ Switch storage verification completed!")
    else:
        print("\n❌ Switch storage verification failed!")
