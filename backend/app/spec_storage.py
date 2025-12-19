# In-memory spec storage for genuine responses
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Global in-memory storage
_spec_storage: Dict[str, Dict] = {}


def save_spec(spec_id: str, spec_data: Dict) -> None:
    """Save spec to in-memory storage"""
    _spec_storage[spec_id] = spec_data
    logger.info(f"💾 Saved spec {spec_id} to memory storage")


def get_spec(spec_id: str) -> Optional[Dict]:
    """Get spec from in-memory storage"""
    spec = _spec_storage.get(spec_id)
    if spec:
        logger.info(f"📖 Retrieved spec {spec_id} from memory storage")
    else:
        logger.debug(f"Spec {spec_id} not in memory storage, will check database")
    return spec


def list_specs() -> Dict[str, Dict]:
    """List all stored specs"""
    return _spec_storage.copy()


def delete_spec(spec_id: str) -> bool:
    """Delete spec from storage"""
    if spec_id in _spec_storage:
        del _spec_storage[spec_id]
        logger.info(f"🗑️ Deleted spec {spec_id} from memory storage")
        return True
    return False
