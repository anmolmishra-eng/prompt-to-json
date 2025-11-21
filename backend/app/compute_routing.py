import asyncio
import os

import httpx

DEVICE_PREFERENCE = os.getenv("DEVICE_PREFERENCE", "auto")
YOTTA_URL = os.getenv("YOTTA_URL", "")
YOTTA_API_KEY = os.getenv("YOTTA_API_KEY", "")


def route(is_heavy: bool) -> str:
    """
    Return 'local' or 'yotta' based on preference and workload size.
    """
    if DEVICE_PREFERENCE == "local":
        return "local"
    if DEVICE_PREFERENCE == "yotta" and YOTTA_URL:
        return "yotta"
    # Default to local if Yotta not configured
    if not YOTTA_URL:
        return "local"
    return "yotta" if is_heavy else "local"


async def run_yotta(job_kind: str, payload: dict):
    """
    Submit a training/inference job to Yotta and poll until completion.
    Your Yotta cluster should expose /submit and /status/{id}.
    """
    if not YOTTA_URL:
        raise RuntimeError("YOTTA_URL not configured")

    headers = {"Authorization": f"Bearer {YOTTA_API_KEY}"} if YOTTA_API_KEY else {}
    async with httpx.AsyncClient(timeout=None) as client:
        sub = await client.post(
            f"{YOTTA_URL}/submit",
            json={"kind": job_kind, "payload": payload},
            headers=headers,
        )
        sub.raise_for_status()
        job = sub.json()
        job_id = job["id"]

        while True:
            st = await client.get(f"{YOTTA_URL}/status/{job_id}", headers=headers)
            st.raise_for_status()
            data = st.json()
            if data["status"] in ("succeeded", "failed"):
                return data
            await asyncio.sleep(5)
