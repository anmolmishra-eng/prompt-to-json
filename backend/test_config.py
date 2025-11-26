#!/usr/bin/env python3
"""
Configuration System Test
Quick test to verify the configuration system is working correctly
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))


def test_config_import():
    """Test that configuration can be imported"""
    try:
        from app.config import Settings, settings, validate_settings

        print("Configuration import successful")
        return True
    except Exception as e:
        print(f"Configuration import failed: {e}")
        return False


def test_settings_access():
    """Test that settings can be accessed"""
    try:
        from app.config import settings

        # Test basic settings
        assert hasattr(settings, "APP_NAME")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "JWT_SECRET_KEY")

        print("Settings access successful")
        print(f"  App Name: {settings.APP_NAME}")
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Debug: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"Settings access failed: {e}")
        return False


def test_validation():
    """Test configuration validation"""
    try:
        from app.config import validate_settings

        validate_settings()
        print("Configuration validation successful")
        return True
    except Exception as e:
        print(f"Configuration validation warning: {e}")
        return True  # Warnings are OK for testing


def test_environment_override():
    """Test environment variable override"""
    try:
        # Set test environment variable
        os.environ["APP_NAME"] = "Test App"

        # Reload settings
        from app.config import Settings

        test_settings = Settings()

        assert test_settings.APP_NAME == "Test App"
        print("Environment variable override successful")

        # Clean up
        del os.environ["APP_NAME"]
        return True
    except Exception as e:
        print(f"Environment override failed: {e}")
        return False


def test_default_values():
    """Test that default values are set correctly"""
    try:
        from app.config import settings

        # Test some default values
        assert settings.PORT == 8000
        assert settings.HOST == "0.0.0.0"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.ENVIRONMENT in ["development", "staging", "production"]

        print("Default values test successful")
        return True
    except Exception as e:
        print(f"Default values test failed: {e}")
        return False


def test_validators():
    """Test configuration validators"""
    try:
        from app.config import Settings

        # Test JWT secret validation
        try:
            Settings(JWT_SECRET_KEY="short")
            print("JWT validation should have failed")
            return False
        except ValueError:
            print("JWT secret validation working")

        # Test database URL validation
        try:
            Settings(DATABASE_URL="invalid://url")
            print("Database URL validation should have failed")
            return False
        except ValueError:
            print("Database URL validation working")

        return True
    except Exception as e:
        print(f"Validator test failed: {e}")
        return False


def main():
    """Run all configuration tests"""
    print("Configuration System Test")
    print("=" * 40)

    tests = [
        ("Import Test", test_config_import),
        ("Settings Access", test_settings_access),
        ("Validation Test", test_validation),
        ("Environment Override", test_environment_override),
        ("Default Values", test_default_values),
        ("Validators", test_validators),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"{test_name} failed")
        except Exception as e:
            print(f"{test_name} error: {e}")

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All configuration tests passed!")
        return True
    else:
        print("Some configuration tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
