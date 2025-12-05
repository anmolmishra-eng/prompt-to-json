#!/usr/bin/env python3
"""
Setup Validation Script
Validates all configuration and dependencies before starting services
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path


class SetupValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []

    def check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.success.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.errors.append(f"❌ Python 3.11+ required, found {version.major}.{version.minor}.{version.micro}")

    def check_environment_file(self):
        """Check if .env file exists and has required variables"""
        env_path = Path("backend/.env")
        if env_path.exists():
            self.success.append("✅ .env file found")

            # Check critical variables
            with open(env_path, 'r') as f:
                content = f.read()

            required_vars = [
                "DATABASE_URL",
                "SUPABASE_URL",
                "SUPABASE_KEY",
                "JWT_SECRET_KEY"
            ]

            for var in required_vars:
                if var in content and not content.split(f"{var}=")[1].split('\n')[0].strip() in ['', 'your-key-here']:
                    self.success.append(f"✅ {var} configured")
                else:
                    self.warnings.append(f"⚠️ {var} not configured or using default value")
        else:
            self.errors.append("❌ .env file not found. Copy from .env.example")

    def check_dependencies(self):
        """Check if all required packages are installed"""
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "httpx",
            "prefect",
            "supabase",
            "torch"
        ]

        for package in required_packages:
            try:
                importlib.import_module(package)
                self.success.append(f"✅ {package} installed")
            except ImportError:
                self.errors.append(f"❌ {package} not installed")

    def check_directories(self):
        """Check if required directories exist"""
        required_dirs = [
            "backend/logs",
            "backend/temp",
            "backend/uploads",
            "backend/cache",
            "backend/data/geometry_outputs",
            "backend/data/mcp_rules"
        ]

        for dir_path in required_dirs:
            path = Path(dir_path)
            if path.exists():
                self.success.append(f"✅ Directory: {dir_path}")
            else:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.success.append(f"✅ Created directory: {dir_path}")
                except Exception as e:
                    self.errors.append(f"❌ Cannot create directory {dir_path}: {e}")

    def check_gpu_availability(self):
        """Check GPU availability"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.success.append(f"✅ GPU available: {gpu_name}")
            else:
                self.warnings.append("⚠️ GPU not available, using CPU mode")
        except ImportError:
            self.warnings.append("⚠️ PyTorch not installed, cannot check GPU")

    def check_external_services(self):
        """Check external service connectivity"""
        import httpx
        import asyncio

        async def check_service(name, url):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        self.success.append(f"✅ {name} reachable")
                    else:
                        self.warnings.append(f"⚠️ {name} returned {response.status_code}")
            except Exception as e:
                self.warnings.append(f"⚠️ {name} not reachable: {e}")

        async def check_all():
            await check_service("Sohum MCP Service", "https://ai-rule-api-w7z5.onrender.com/health")

        try:
            asyncio.run(check_all())
        except Exception as e:
            self.warnings.append(f"⚠️ Cannot check external services: {e}")

    def check_ports(self):
        """Check if required ports are available"""
        import socket

        ports = [8000, 8003, 4200]
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result != 0:
                self.success.append(f"✅ Port {port} available")
            else:
                self.warnings.append(f"⚠️ Port {port} already in use")

    def run_validation(self):
        """Run all validation checks"""
        print("=" * 70)
        print("🔍 BHIV AI Assistant - Setup Validation")
        print("=" * 70)

        print("\n📋 Checking system requirements...")
        self.check_python_version()

        print("\n📁 Checking files and directories...")
        self.check_environment_file()
        self.check_directories()

        print("\n📦 Checking dependencies...")
        self.check_dependencies()

        print("\n🖥️ Checking hardware...")
        self.check_gpu_availability()

        print("\n🌐 Checking external services...")
        self.check_external_services()

        print("\n🔌 Checking ports...")
        self.check_ports()

        # Print summary
        print("\n" + "=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)

        if self.success:
            print(f"\n✅ SUCCESS ({len(self.success)} items):")
            for item in self.success:
                print(f"  {item}")

        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)} items):")
            for item in self.warnings:
                print(f"  {item}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)} items):")
            for item in self.errors:
                print(f"  {item}")

        print("\n" + "=" * 70)

        if self.errors:
            print("❌ Setup validation failed. Please fix errors before proceeding.")
            return False
        elif self.warnings:
            print("⚠️ Setup validation completed with warnings. System should work but some features may be limited.")
            return True
        else:
            print("✅ Setup validation passed! System is ready to start.")
            return True


def main():
    """Main validation runner"""
    # Change to project directory
    os.chdir(Path(__file__).parent)

    validator = SetupValidator()
    success = validator.run_validation()

    if success:
        print("\n🚀 Next steps:")
        print("1. Run: start_all_services.bat")
        print("2. Wait for all services to start (2-3 minutes)")
        print("3. Run: python test_complete_system.py")
        print("4. Access: http://localhost:8000/docs")
    else:
        print("\n🔧 Fix the errors above and run this script again.")

    return success


if __name__ == "__main__":
    main()
