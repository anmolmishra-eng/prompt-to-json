#!/usr/bin/env python3
"""
Create test user for BHIV endpoint testing
"""
import asyncio

from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session


async def create_test_user():
    """Create test user in database"""
    db = next(get_db())

    # Check if user exists
    existing_user = db.query(User).filter(User.id == "test_user_123").first()
    if existing_user:
        print("Test user already exists")
        return

    # Create new user
    test_user = User(
        id="test_user_123",
        username="testuser123",
        email="test@bhiv.com",
        password_hash="dummy_hash",
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    print("Test user created successfully")
    db.close()


if __name__ == "__main__":
    asyncio.run(create_test_user())
