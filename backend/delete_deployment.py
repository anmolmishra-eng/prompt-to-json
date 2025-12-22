import asyncio

from prefect.client.orchestration import get_client


async def delete_first_deployment():
    async with get_client() as client:
        deployments = await client.read_deployments()
        if deployments:
            print(f"Deleting: {deployments[0].name}")
            await client.delete_deployment(deployments[0].id)
            print("Deleted successfully")
        else:
            print("No deployments found")


if __name__ == "__main__":
    asyncio.run(delete_first_deployment())
