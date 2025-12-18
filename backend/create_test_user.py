#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uuid

from app.auth import hash_password
from app.database import SessionLocal
from app.models import User


def create_test_user():
    db = SessionLocal()
    try:
        # Create test user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username="admin",
            email="admin@bhiv.com",
            password_hash=hash_password("bhiv2024"),
            full_name="Admin User",
            is_active=True,
        )

        db.add(user)
        db.commit()

        print(f"Created user with ID: {user_id}")
        print(f"Username: admin")
        print(f"Password: bhiv2024")
        return user_id

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
