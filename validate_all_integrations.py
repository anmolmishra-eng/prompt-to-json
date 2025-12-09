"""
Validate All BHIV Integrations
Check that all files are properly integrated and working
"""

import os
import sys
import importlib.util
from pathlib import Path

class IntegrationValidator:
    """Validate all BHIV integrations"""

    def __init__(self):
        self.backend_path = Path("backend")
        self.results = {
            "file_existence": {},
            "import_validation": {},
            "integration_check": {},
            "api_endpoints": {}
        }

    def validate_all(self):
        """Run all validation checks"""

        print("🔍 BHIV Integration Validation")
        print("=" * 50)

        self.check_file_existence()
        self.validate_imports()
        self.check_integrations()
        self.validate_api_endpoints()

        self.print_summary()

    def check_file_existence(self):
        """Check all required files exist"""

        print("\n1. Checking File Existence...")

        required_files = {
            # New API files
            "app/api/mcp_integration.py": "MCP Integration API",
            "app/api/geometry_generator.py": "Geometry Generator API",
            "app/api/monitoring_system.py": "Monitoring System API",

            # Multi-city RL
            "app/multi_city/rl_feedback_integration.py": "Multi-city RL Feedback",

            # Enhanced workflows
            "app/bhiv_assistant/workflows/mcp_compliance_flow.py": "MCP Compliance Workflow",
            "app/bhiv_assistant/workflows/rl_integration_flows.py": "RL Integration Workflow",
            "app/bhiv_assistant/workflows/notification_flows.py": "Notification Workflow",

            # Configuration
            ".env.example": "Environment Configuration",

            # Main integration
            "app/main.py": "Main FastAPI Application"
        }

        for file_path, description in required_files.items():
            full_path = self.backend_path / file_path
            exists = full_path.exists()

            self.results["file_existence"][file_path] = {
                "exists": exists,
                "description": description
            }

            status = "✅" if exists else "❌"
            print(f"{status} {description}: {file_path}")

    def validate_imports(self):
        """Validate that all imports work correctly"""

        print("\n2. Validating Imports...")

        import_tests = {
            "MCP Integration": "from app.api import mcp_integration",
            "Geometry Generator": "from app.api import geometry_generator",
            "Monitoring System": "from app.api import monitoring_system",
            "Multi-city RL": "from app.multi_city.rl_feedback_integration import multi_city_rl",
            "MCP Workflow": "from app.bhiv_assistant.workflows.mcp_compliance_flow import mcp_compliance_flow",
            "RL Workflow": "from app.bhiv_assistant.workflows.rl_integration_flows import rl_optimization_flow",
            "Notification Workflow": "from app.bhiv_assistant.workflows.notification_flows import system_health_monitoring_flow"
        }

        # Change to backend directory for imports
        original_path = sys.path.copy()
        backend_abs_path = os.path.abspath("backend")
        if backend_abs_path not in sys.path:
            sys.path.insert(0, backend_abs_path)

        for name, import_statement in import_tests.items():
            try:
                exec(import_statement)
                self.results["import_validation"][name] = {"success": True, "error": None}
                print(f"✅ {name}: Import successful")
            except Exception as e:
                self.results["import_validation"][name] = {"success": False, "error": str(e)}
                print(f"❌ {name}: Import failed - {e}")

        # Restore original path
        sys.path = original_path

    def check_integrations(self):
        """Check that integrations are properly connected"""

        print("\n3. Checking Integrations...")

        # Check main.py has all new imports
        main_py_path = self.backend_path / "app/main.py"

        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                main_content = f.read()

            required_imports = [
                "mcp_integration",
                "geometry_generator",
                "monitoring_system",
                "multi_city_rl"
            ]

            missing_imports = []
            for imp in required_imports:
                if imp not in main_content:
                    missing_imports.append(imp)

            if not missing_imports:
                print("✅ Main.py: All new imports present")
                self.results["integration_check"]["main_imports"] = {"success": True, "missing": []}
            else:
                print(f"❌ Main.py: Missing imports - {missing_imports}")
                self.results["integration_check"]["main_imports"] = {"success": False, "missing": missing_imports}

            # Check router inclusions
            required_routers = [
                "mcp_integration.router",
                "geometry_generator.router",
                "monitoring_system.router"
            ]

            missing_routers = []
            for router in required_routers:
                if router not in main_content:
                    missing_routers.append(router)

            if not missing_routers:
                print("✅ Main.py: All new routers included")
                self.results["integration_check"]["main_routers"] = {"success": True, "missing": []}
            else:
                print(f"❌ Main.py: Missing routers - {missing_routers}")
                self.results["integration_check"]["main_routers"] = {"success": False, "missing": missing_routers}

        # Check BHIV assistant integration
        bhiv_assistant_path = self.backend_path / "app/api/bhiv_assistant.py"

        if bhiv_assistant_path.exists():
            with open(bhiv_assistant_path, 'r') as f:
                bhiv_content = f.read()

            integrations_check = {
                "monitoring": "monitoring_system" in bhiv_content,
                "geometry_api": "/api/v1/geometry/generate" in bhiv_content,
                "mcp_api": "/api/v1/mcp/check" in bhiv_content,
                "performance_tracking": "@track_performance" in bhiv_content
            }

            for integration, present in integrations_check.items():
                status = "✅" if present else "❌"
                print(f"{status} BHIV Assistant: {integration} integration")
                self.results["integration_check"][f"bhiv_{integration}"] = present

    def validate_api_endpoints(self):
        """Validate API endpoint definitions"""

        print("\n4. Validating API Endpoints...")

        endpoint_files = {
            "MCP Integration": self.backend_path / "app/api/mcp_integration.py",
            "Geometry Generator": self.backend_path / "app/api/geometry_generator.py",
            "Monitoring System": self.backend_path / "app/api/monitoring_system.py"
        }

        expected_endpoints = {
            "MCP Integration": ["/check", "/cities", "/feedback"],
            "Geometry Generator": ["/generate", "/download", "/list"],
            "Monitoring System": ["/metrics", "/alert/test"]
        }

        for service, file_path in endpoint_files.items():
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()

                endpoints = expected_endpoints[service]
                found_endpoints = []
                missing_endpoints = []

                for endpoint in endpoints:
                    if f'"{endpoint}"' in content or f"'{endpoint}'" in content:
                        found_endpoints.append(endpoint)
                    else:
                        missing_endpoints.append(endpoint)

                if not missing_endpoints:
                    print(f"✅ {service}: All endpoints defined")
                    self.results["api_endpoints"][service] = {
                        "success": True,
                        "found": found_endpoints,
                        "missing": []
                    }
                else:
                    print(f"❌ {service}: Missing endpoints - {missing_endpoints}")
                    self.results["api_endpoints"][service] = {
                        "success": False,
                        "found": found_endpoints,
                        "missing": missing_endpoints
                    }
            else:
                print(f"❌ {service}: File not found")
                self.results["api_endpoints"][service] = {
                    "success": False,
                    "found": [],
                    "missing": expected_endpoints[service]
                }

    def print_summary(self):
        """Print validation summary"""

        print("\n" + "=" * 60)
        print("📋 INTEGRATION VALIDATION SUMMARY")
        print("=" * 60)

        # File existence summary
        total_files = len(self.results["file_existence"])
        existing_files = sum(1 for f in self.results["file_existence"].values() if f["exists"])
        print(f"\n📁 Files: {existing_files}/{total_files} exist")

        # Import validation summary
        total_imports = len(self.results["import_validation"])
        successful_imports = sum(1 for i in self.results["import_validation"].values() if i["success"])
        print(f"📦 Imports: {successful_imports}/{total_imports} successful")

        # Integration check summary
        integration_checks = [
            self.results["integration_check"].get("main_imports", {}).get("success", False),
            self.results["integration_check"].get("main_routers", {}).get("success", False),
            self.results["integration_check"].get("bhiv_monitoring", False),
            self.results["integration_check"].get("bhiv_geometry_api", False),
            self.results["integration_check"].get("bhiv_mcp_api", False)
        ]
        successful_integrations = sum(integration_checks)
        print(f"🔗 Integrations: {successful_integrations}/{len(integration_checks)} connected")

        # API endpoints summary
        total_services = len(self.results["api_endpoints"])
        successful_services = sum(1 for s in self.results["api_endpoints"].values() if s["success"])
        print(f"🌐 API Services: {successful_services}/{total_services} complete")

        # Overall status
        total_checks = existing_files + successful_imports + successful_integrations + successful_services
        max_checks = total_files + total_imports + len(integration_checks) + total_services

        success_rate = (total_checks / max_checks) * 100 if max_checks > 0 else 0

        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            print("🎉 EXCELLENT: All integrations working perfectly!")
        elif success_rate >= 80:
            print("✅ GOOD: Most integrations working, minor issues to fix")
        elif success_rate >= 60:
            print("⚠️  FAIR: Several integrations need attention")
        else:
            print("❌ POOR: Major integration issues need fixing")

        print("=" * 60)

        # Detailed issues
        if success_rate < 100:
            print("\n🔧 Issues to Fix:")

            # Missing files
            missing_files = [f for f, data in self.results["file_existence"].items() if not data["exists"]]
            if missing_files:
                print(f"📁 Missing files: {', '.join(missing_files)}")

            # Failed imports
            failed_imports = [name for name, data in self.results["import_validation"].items() if not data["success"]]
            if failed_imports:
                print(f"📦 Failed imports: {', '.join(failed_imports)}")

            # Integration issues
            if not self.results["integration_check"].get("main_imports", {}).get("success", True):
                missing = self.results["integration_check"]["main_imports"].get("missing", [])
                print(f"🔗 Missing main.py imports: {', '.join(missing)}")

            if not self.results["integration_check"].get("main_routers", {}).get("success", True):
                missing = self.results["integration_check"]["main_routers"].get("missing", [])
                print(f"🔗 Missing main.py routers: {', '.join(missing)}")

            # API issues
            incomplete_apis = [name for name, data in self.results["api_endpoints"].items() if not data["success"]]
            if incomplete_apis:
                print(f"🌐 Incomplete APIs: {', '.join(incomplete_apis)}")


def main():
    """Run validation"""
    validator = IntegrationValidator()
    validator.validate_all()


if __name__ == "__main__":
    main()
