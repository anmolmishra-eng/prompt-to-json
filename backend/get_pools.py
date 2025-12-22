import asyncio

from prefect.client.orchestration import get_client


async def get_pools():
    async with get_client() as client:
        pools = await client.read_work_pools()
        for p in pools:
            print(f"Name: '{p.name}' | Type: {p.type}")


if __name__ == "__main__":
    asyncio.run(get_pools())
