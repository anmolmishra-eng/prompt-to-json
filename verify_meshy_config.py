"""Quick verification that Meshy API key is loaded"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

print("🔍 Verifying Meshy AI Configuration\n")

# Check environment variable
meshy_key = os.getenv("MESHY_API_KEY")
if meshy_key:
    print(f"✅ MESHY_API_KEY found in environment")
    print(f"   Key: {meshy_key[:10]}...{meshy_key[-4:]}")
else:
    print("❌ MESHY_API_KEY not found in environment")

# Check config
try:
    from app.config import settings
    if settings.MESHY_API_KEY:
        print(f"✅ MESHY_API_KEY loaded in settings")
        print(f"   Key: {settings.MESHY_API_KEY[:10]}...{settings.MESHY_API_KEY[-4:]}")
    else:
        print("❌ MESHY_API_KEY not in settings")
except Exception as e:
    print(f"⚠️  Could not load settings: {e}")

# Check other 3D API keys
print("\n📊 Other 3D API Keys:")
tripo_key = os.getenv("TRIPO_API_KEY")
if tripo_key:
    print(f"   Tripo AI: {tripo_key[:10]}...{tripo_key[-4:]}")
else:
    print("   Tripo AI: Not configured")

hf_key = os.getenv("HUGGINGFACE_API_KEY")
if hf_key:
    print(f"   HuggingFace: {hf_key[:10]}...{hf_key[-4:]}")
else:
    print("   HuggingFace: Not configured")

print("\n✨ Configuration check complete!")
