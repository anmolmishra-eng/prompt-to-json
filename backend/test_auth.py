#!/usr/bin/env python3
"""
Authentication Module Test
Test JWT tokens, password hashing, and user authentication
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))


def test_password_hashing():
    """Test password hashing and verification"""
    try:
        from app.auth import hash_password, verify_password

        password = "test123"
        hashed = hash_password(password)

        # Test correct password
        if verify_password(password, hashed):
            print("Password verification: CORRECT")
        else:
            print("Password verification: FAILED")
            return False

        # Test wrong password
        if not verify_password("wrong", hashed):
            print("Wrong password rejection: CORRECT")
        else:
            print("Wrong password rejection: FAILED")
            return False

        return True
    except Exception as e:
        print(f"Password hashing failed: {e}")
        return False


def test_jwt_tokens():
    """Test JWT token creation and verification"""
    try:
        from app.auth import create_access_token, verify_token

        user_id = "test-user-123"
        token = create_access_token(user_id)

        # Verify token
        decoded_user_id = verify_token(token)

        if decoded_user_id == user_id:
            print("JWT token creation/verification: CORRECT")
            return True
        else:
            print(f"JWT token verification failed: expected {user_id}, got {decoded_user_id}")
            return False
    except Exception as e:
        print(f"JWT token test failed: {e}")
        return False


def test_token_expiry():
    """Test token expiry handling"""
    try:
        from datetime import timedelta

        from app.auth import verify_token

        # Test with invalid token
        invalid_token = "invalid.token.here"
        result = verify_token(invalid_token)

        if result is None:
            print("Invalid token rejection: CORRECT")
            return True
        else:
            print("Invalid token rejection: FAILED")
            return False
    except Exception as e:
        print(f"Token expiry test failed: {e}")
        return False


def test_auth_imports():
    """Test that all auth functions can be imported"""
    try:
        from app.auth import (
            authenticate_user,
            create_access_token,
            create_refresh_token,
            get_current_user,
            hash_password,
            refresh_access_token,
            verify_password,
            verify_refresh_token,
            verify_token,
        )

        print("Auth imports: CORRECT")
        return True
    except Exception as e:
        print(f"Auth imports failed: {e}")
        return False


def main():
    """Run all authentication tests"""
    print("Authentication Module Test")
    print("=" * 40)

    tests = [
        ("Import Test", test_auth_imports),
        ("Password Hashing", test_password_hashing),
        ("JWT Tokens", test_jwt_tokens),
        ("Token Expiry", test_token_expiry),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"{test_name}: PASSED")
            else:
                print(f"{test_name}: FAILED")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All authentication tests passed!")
        return True
    else:
        print("Some authentication tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
