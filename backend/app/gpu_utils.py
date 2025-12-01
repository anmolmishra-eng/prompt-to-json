"""
GPU Utilities for AI Processing
Provides consistent GPU detection across the application
"""
from typing import Optional, Tuple

from app.gpu_detector import gpu_detector


def get_optimal_device() -> str:
    """Get the optimal device for AI processing"""
    return gpu_detector.get_device()


def get_gpu_memory_info() -> Optional[dict]:
    """Get GPU memory information"""
    if not gpu_detector.is_gpu_available():
        return None

    try:
        import torch

        if torch.cuda.is_available():
            device_id = 0
            return {
                "total": torch.cuda.get_device_properties(device_id).total_memory,
                "allocated": torch.cuda.memory_allocated(device_id),
                "cached": torch.cuda.memory_reserved(device_id),
                "free": torch.cuda.get_device_properties(device_id).total_memory
                - torch.cuda.memory_allocated(device_id),
            }
    except Exception:
        pass

    return None


def ensure_gpu_available() -> Tuple[bool, str]:
    """Ensure GPU is available for processing"""
    if gpu_detector.is_gpu_available():
        return True, "cuda"
    else:
        return False, "cpu"


def get_device_info() -> dict:
    """Get comprehensive device information"""
    gpu_info = gpu_detector.detect_gpu()

    return {
        "device": gpu_detector.get_device(),
        "gpu_available": gpu_detector.is_gpu_available(),
        "gpu_count": gpu_info["gpu_count"],
        "detection_method": gpu_info["detection_method"],
        "best_gpu": gpu_detector.get_best_gpu(),
    }
