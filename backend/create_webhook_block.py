#!/usr/bin/env python3
"""
Create Prefect Webhook Block for BHIV
"""

import asyncio

from prefect.blocks.webhook import Webhook


async def create_bhiv_webhook():
    """Create and save BHIV webhook block"""

    # Create webhook block - Update this URL after creating webhook in Prefect Cloud UI
    webhook_block = Webhook(
        url="PASTE_YOUR_WEBHOOK_URL_HERE",  # Replace with the URL you copied from Step 5
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY_HERE",  # Optional: Add if needed
        },
    )

    # Save the block
    await webhook_block.save("bhiv-webhook", overwrite=True)
    print("BHIV webhook block created and saved as 'bhiv-webhook'")

    # Test the webhook
    try:
        response = await webhook_block.call(
            payload={"event": "test", "message": "BHIV webhook test", "timestamp": "2025-12-22T16:30:00Z"}
        )
        print(f"Webhook test successful: {response.status_code}")
    except Exception as e:
        print(f"Webhook test failed: {e}")


if __name__ == "__main__":
    asyncio.run(create_bhiv_webhook())
