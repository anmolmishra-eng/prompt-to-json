#!/usr/bin/env python3
"""
Test BHIV webhook integration
"""

import asyncio

from prefect.blocks.webhook import Webhook


async def test_webhook():
    """Test the bhiv-webhook block"""
    try:
        # Load the webhook block
        webhook_block = await Webhook.load("bhiv-webhook")
        print("Webhook block loaded successfully")

        # Test payload
        test_payload = {
            "event": "bhiv_test",
            "design_id": "test_design_123",
            "status": "completed",
            "message": "BHIV webhook integration test",
            "timestamp": "2025-12-22T22:50:00Z",
        }

        # Send test webhook
        response = await webhook_block.call(payload=test_payload)
        print(f"Webhook test successful!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

    except Exception as e:
        print(f"Webhook test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_webhook())
