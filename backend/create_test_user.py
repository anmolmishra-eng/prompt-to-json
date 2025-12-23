#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_user():
    db = next(get_db())

    # Check if test user exists
    existing = db.query(User).filter(User.username == "testflow").first()
    if existing:
        print("Test user 'testflow' already exists")
        return

    # Create new test user
    hashed_password = pwd_context.hash("test123")

    new_user = User(
        id="testflow_id", username="testflow", email="testflow@example.com", hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    print("Created test user: testflow / test123")


if __name__ == "__main__":
    create_test_user()
