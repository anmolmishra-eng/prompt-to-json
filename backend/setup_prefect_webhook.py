#!/usr/bin/env python3
"""
Prefect Webhook Configuration Guide
"""

print("PREFECT WEBHOOK CONFIGURATION")
print("=" * 50)

print("\n1. LOGIN TO PREFECT CLOUD:")
print("   - Go to: https://app.prefect.cloud/")
print("   - Sign in with your account")

print("\n2. CREATE WEBHOOK:")
print("   - Navigate to: Webhooks section")
print("   - Click 'Create Webhook'")
print("   - Name: 'BHIV-AI-Assistant'")
print("   - Description: 'BHIV design completion notifications'")

print("\n3. GET WEBHOOK URL:")
print("   - Copy the generated webhook URL")
print("   - Format: https://api.prefect.cloud/hooks/[your-webhook-id]")

print("\n4. ADD TO .ENV FILE:")
print("   Add this line to your .env file:")
print("   PREFECT_WEBHOOK_URL=https://api.prefect.cloud/hooks/[your-webhook-id]")

print("\n5. RESTART SERVER:")
print("   Restart your FastAPI server to load the new configuration")

print("\nALTERNATIVE - QUICK TEST:")
print("Set a test webhook URL to verify functionality:")
print("PREFECT_WEBHOOK_URL=https://webhook.site/[unique-id]")
print("(Get unique-id from https://webhook.site/)")
