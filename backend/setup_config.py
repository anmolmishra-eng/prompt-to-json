#!/usr/bin/env python3
"""
Configuration Setup Utility
Interactive setup for Design Engine API Backend configuration
"""

import json
import os
import secrets
import string
from pathlib import Path
from typing import Any, Dict


class ConfigSetup:
    """Interactive configuration setup"""

    def __init__(self):
        self.config = {}
        self.env_file = Path(".env")
        self.example_file = Path(".env.example")

    def generate_secret(self, length: int = 32) -> str:
        """Generate a secure random secret"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def prompt_input(
        self, key: str, description: str, default: str = "", required: bool = True, secret: bool = False
    ) -> str:
        """Prompt user for input with validation"""
        prompt = f"{description}"
        if default:
            prompt += f" (default: {default if not secret else '***'})"
        if required:
            prompt += " [REQUIRED]"
        prompt += ": "

        while True:
            value = input(prompt).strip()
            if not value and default:
                return default
            elif not value and required:
                print("❌ This field is required!")
                continue
            elif not value and not required:
                return ""
            else:
                return value

    def prompt_boolean(self, key: str, description: str, default: bool = True) -> bool:
        """Prompt for boolean input"""
        default_str = "Y/n" if default else "y/N"
        prompt = f"{description} ({default_str}): "

        while True:
            value = input(prompt).strip().lower()
            if not value:
                return default
            elif value in ["y", "yes", "true", "1"]:
                return True
            elif value in ["n", "no", "false", "0"]:
                return False
            else:
                print("❌ Please enter y/n, yes/no, true/false, or 1/0")

    def setup_basic_config(self):
        """Setup basic application configuration"""
        print("\n🚀 Basic Application Configuration")
        print("-" * 40)

        self.config.update(
            {
                "APP_NAME": self.prompt_input("APP_NAME", "Application name", "Design Engine API Backend", False),
                "ENVIRONMENT": self.prompt_input(
                    "ENVIRONMENT", "Environment (development/staging/production)", "development", False
                ),
                "DEBUG": str(self.prompt_boolean("DEBUG", "Enable debug mode", True)).lower(),
                "PORT": self.prompt_input("PORT", "Server port", "8000", False),
            }
        )

    def setup_database(self):
        """Setup database configuration"""
        print("\n🗄️  Database Configuration")
        print("-" * 40)

        db_type = input("Database type (1=PostgreSQL, 2=SQLite) [1]: ").strip() or "1"

        if db_type == "2":
            db_path = self.prompt_input("DB_PATH", "SQLite database path", "app.db", False)
            self.config["DATABASE_URL"] = f"sqlite:///{db_path}"
        else:
            print("PostgreSQL Configuration:")
            host = self.prompt_input("DB_HOST", "Database host", "localhost")
            port = self.prompt_input("DB_PORT", "Database port", "5432", False)
            user = self.prompt_input("DB_USER", "Database user", "postgres")
            password = self.prompt_input("DB_PASSWORD", "Database password", "", True, True)
            database = self.prompt_input("DB_NAME", "Database name", "design_engine")

            self.config["DATABASE_URL"] = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def setup_supabase(self):
        """Setup Supabase configuration"""
        print("\n☁️  Supabase Configuration")
        print("-" * 40)

        use_supabase = self.prompt_boolean("USE_SUPABASE", "Use Supabase for storage", True)

        if use_supabase:
            self.config.update(
                {
                    "SUPABASE_URL": self.prompt_input(
                        "SUPABASE_URL", "Supabase project URL", "https://your-project.supabase.co"
                    ),
                    "SUPABASE_KEY": self.prompt_input("SUPABASE_KEY", "Supabase anon key", "", True, True),
                    "SUPABASE_SERVICE_KEY": self.prompt_input(
                        "SUPABASE_SERVICE_KEY", "Supabase service key (optional)", "", False, True
                    ),
                }
            )
        else:
            print("⚠️  Skipping Supabase - file storage will be disabled")

    def setup_jwt(self):
        """Setup JWT configuration"""
        print("\n🔐 JWT Authentication Configuration")
        print("-" * 40)

        generate_secret = self.prompt_boolean("GENERATE_JWT_SECRET", "Generate secure JWT secret", True)

        if generate_secret:
            jwt_secret = self.generate_secret(32)
            print(f"✓ Generated secure JWT secret: {jwt_secret[:8]}...")
        else:
            jwt_secret = self.prompt_input("JWT_SECRET_KEY", "JWT secret key (min 32 chars)", "", True, True)
            if len(jwt_secret) < 32:
                print("⚠️  Warning: JWT secret should be at least 32 characters for security")

        self.config.update(
            {
                "JWT_SECRET_KEY": jwt_secret,
                "JWT_SECRET": jwt_secret,
                "JWT_EXPIRATION_HOURS": self.prompt_input(
                    "JWT_EXPIRATION_HOURS", "JWT token lifetime (hours)", "24", False
                ),
            }
        )

    def setup_external_services(self):
        """Setup external services"""
        print("\n🌐 External Services Configuration")
        print("-" * 40)

        # Sohum's MCP Service
        use_mcp = self.prompt_boolean("USE_MCP", "Enable Sohum's MCP compliance service", True)
        if use_mcp:
            self.config.update(
                {
                    "SOHUM_MCP_URL": self.prompt_input(
                        "SOHUM_MCP_URL", "Sohum MCP service URL", "https://ai-rule-api-w7z5.onrender.com"
                    ),
                    "SOHUM_API_KEY": self.prompt_input("SOHUM_API_KEY", "Sohum API key (optional)", "", False, True),
                }
            )

        # Ranjeet's RL Service
        use_rl = self.prompt_boolean("USE_RL", "Enable Ranjeet's RL service", True)
        if use_rl:
            self.config.update(
                {
                    "RANJEET_RL_URL": self.prompt_input(
                        "RANJEET_RL_URL", "Ranjeet RL service URL", "http://localhost:8001"
                    ),
                    "RANJEET_API_KEY": self.prompt_input(
                        "RANJEET_API_KEY", "Ranjeet API key (optional)", "", False, True
                    ),
                }
            )

    def setup_ai_models(self):
        """Setup AI/ML model configuration"""
        print("\n🤖 AI/ML Model Configuration")
        print("-" * 40)

        provider = input("LM Provider (1=Local GPU, 2=Yotta Cloud, 3=OpenAI) [1]: ").strip() or "1"

        if provider == "1":
            self.config.update(
                {
                    "LM_PROVIDER": "local",
                    "LOCAL_GPU_ENABLED": "true",
                    "LOCAL_GPU_DEVICE": self.prompt_input("LOCAL_GPU_DEVICE", "CUDA device", "cuda:0", False),
                }
            )
        elif provider == "2":
            self.config.update(
                {
                    "LM_PROVIDER": "yotta",
                    "YOTTA_API_KEY": self.prompt_input("YOTTA_API_KEY", "Yotta API key", "", True, True),
                    "YOTTA_URL": self.prompt_input(
                        "YOTTA_URL", "Yotta API URL", "https://api.yotta.ai/v1/inference", False
                    ),
                }
            )
        elif provider == "3":
            self.config.update(
                {
                    "LM_PROVIDER": "openai",
                    "OPENAI_API_KEY": self.prompt_input("OPENAI_API_KEY", "OpenAI API key", "", True, True),
                }
            )

    def setup_monitoring(self):
        """Setup monitoring configuration"""
        print("\n📊 Monitoring Configuration")
        print("-" * 40)

        # Sentry
        use_sentry = self.prompt_boolean("USE_SENTRY", "Enable Sentry error tracking", False)
        if use_sentry:
            self.config["SENTRY_DSN"] = self.prompt_input("SENTRY_DSN", "Sentry DSN", "", True, True)

        # Metrics
        self.config["METRICS_ENABLED"] = str(
            self.prompt_boolean("METRICS_ENABLED", "Enable Prometheus metrics", True)
        ).lower()

    def setup_security(self):
        """Setup security configuration"""
        print("\n🔒 Security Configuration")
        print("-" * 40)

        # Encryption key
        generate_encryption = self.prompt_boolean("GENERATE_ENCRYPTION_KEY", "Generate encryption key", True)
        if generate_encryption:
            encryption_key = self.generate_secret(32)
            self.config["ENCRYPTION_KEY"] = encryption_key
            print(f"✓ Generated encryption key: {encryption_key[:8]}...")

        # Demo credentials
        self.config.update(
            {
                "DEMO_USERNAME": self.prompt_input("DEMO_USERNAME", "Demo username", "admin", False),
                "DEMO_PASSWORD": self.prompt_input("DEMO_PASSWORD", "Demo password", "bhiv2024", False),
            }
        )

    def write_env_file(self):
        """Write configuration to .env file"""
        print(f"\n💾 Writing configuration to {self.env_file}")

        # Backup existing .env file
        if self.env_file.exists():
            backup_file = Path(f".env.backup.{secrets.token_hex(4)}")
            self.env_file.rename(backup_file)
            print(f"✓ Backed up existing .env to {backup_file}")

        # Write new .env file
        with open(self.env_file, "w") as f:
            f.write("# Design Engine API Backend Configuration\n")
            f.write("# Generated by setup_config.py\n\n")

            for key, value in self.config.items():
                f.write(f"{key}={value}\n")

        print(f"✓ Configuration written to {self.env_file}")

    def print_summary(self):
        """Print configuration summary"""
        print("\n" + "=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)

        print(f"Environment: {self.config.get('ENVIRONMENT', 'development')}")
        print(f"Database: {'PostgreSQL' if 'postgresql://' in self.config.get('DATABASE_URL', '') else 'SQLite'}")
        print(f"Supabase: {'Enabled' if 'SUPABASE_URL' in self.config else 'Disabled'}")
        print(f"LM Provider: {self.config.get('LM_PROVIDER', 'local')}")
        print(f"Monitoring: {'Enabled' if self.config.get('SENTRY_DSN') else 'Basic'}")

        print(f"\n📁 Configuration file: {self.env_file.absolute()}")
        print("\n🚀 Next steps:")
        print("  1. Review your .env file")
        print("  2. Run: python validate_config.py")
        print("  3. Start the server: python -m uvicorn app.main:app --reload")

    def run_interactive_setup(self):
        """Run the interactive setup process"""
        print("🎯 Design Engine API Backend Configuration Setup")
        print("=" * 60)
        print("This wizard will help you configure your backend environment.")
        print("Press Ctrl+C at any time to cancel.\n")

        try:
            self.setup_basic_config()
            self.setup_database()
            self.setup_supabase()
            self.setup_jwt()
            self.setup_external_services()
            self.setup_ai_models()
            self.setup_monitoring()
            self.setup_security()

            self.write_env_file()
            self.print_summary()

            return True

        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False


def main():
    """Main setup function"""
    setup = ConfigSetup()

    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--quick":
        # Quick setup with defaults
        print("🚀 Quick setup with defaults...")
        setup.config = {
            "APP_NAME": "Design Engine API Backend",
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "PORT": "8000",
            "DATABASE_URL": "sqlite:///app.db",
            "JWT_SECRET_KEY": setup.generate_secret(32),
            "JWT_SECRET": setup.generate_secret(32),
            "SOHUM_MCP_URL": "https://ai-rule-api-w7z5.onrender.com",
            "RANJEET_RL_URL": "http://localhost:8001",
            "LM_PROVIDER": "local",
            "LOCAL_GPU_ENABLED": "true",
            "METRICS_ENABLED": "true",
            "DEMO_USERNAME": "admin",
            "DEMO_PASSWORD": "bhiv2024",
        }
        setup.write_env_file()
        setup.print_summary()
    else:
        # Interactive setup
        success = setup.run_interactive_setup()
        return 0 if success else 1


if __name__ == "__main__":
    exit(main())
