# Compute Routing Configuration

## Local vs. Cloud Routing

### Decision Logic

```
┌─────────────────────────┐
│     Received Request    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Check Job Complexity  │
│      - Spec size        │
│      - LM steps         │
│      - RL training      │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
   Simple        Complex
   <100ms        >500ms
      │             │
      ▼             ▼
    LOCAL         YOTTA
     GPU          Cloud
  RTX-3060       TPU/GPU
```

### Configuration

```python
# app/config.py
class ComputeConfig:
    # Local inference settings
    LOCAL_GPU_ENABLED = os.getenv("LOCAL_GPU_ENABLED", "true").lower() == "true"
    LOCAL_GPU_TYPE = os.getenv("LOCAL_GPU_TYPE", "rtx3060")  # RTX-3060
    LOCAL_BATCH_SIZE = int(os.getenv("LOCAL_BATCH_SIZE", "1"))
    LOCAL_MAX_TOKENS = int(os.getenv("LOCAL_MAX_TOKENS", "512"))

    # Yotta cloud settings
    YOTTA_ENABLED = os.getenv("YOTTA_ENABLED", "true").lower() == "true"
    YOTTA_API_KEY = os.getenv("YOTTA_API_KEY")
    YOTTA_ENDPOINT = os.getenv("YOTTA_ENDPOINT", "https://api.yotta.cloud")

    # Routing thresholds
    ROUTE_TO_CLOUD_IF_TOKENS_EXCEED = 1000
    ROUTE_TO_CLOUD_IF_STEPS_EXCEED = 10000
    ROUTE_TO_CLOUD_IF_COMPLEXITY_SCORE_EXCEEDS = 50

    # Fallback
    FALLBACK_TO_LOCAL = True
```

## Usage

```python
# app/compute_routing.py
from app.config import ComputeConfig as cfg

def route(job_complexity: int) -> str:
    """
    Route job to local GPU or Yotta cloud

    job_complexity: 0-100 score
    returns: 'local' or 'yotta'
    """

    if not cfg.LOCAL_GPU_ENABLED and cfg.YOTTA_ENABLED:
        return "yotta"

    if job_complexity > cfg.ROUTE_TO_CLOUD_IF_COMPLEXITY_SCORE_EXCEEDS:
        if cfg.YOTTA_ENABLED:
            return "yotta"
        elif cfg.FALLBACK_TO_LOCAL:
            return "local"

    if cfg.LOCAL_GPU_ENABLED:
        return "local"

    return "yotta" if cfg.YOTTA_ENABLED else "local"


async def run_yotta(job_type: str, params: dict) -> dict:
    """
    Submit job to Yotta cloud
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{cfg.YOTTA_ENDPOINT}/submit",
            json={"job_type": job_type, "params": params},
            headers={"Authorization": f"Bearer {cfg.YOTTA_API_KEY}"},
            timeout=300.0
        )

        return response.json()
```
