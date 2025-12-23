#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session


def check_users():
    db = next(get_db())
    users = db.query(User).all()

    print("EXISTING USERS:")
    for user in users:
        print(f"- Username: {user.username}")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print()


if __name__ == "__main__":
    check_users()
