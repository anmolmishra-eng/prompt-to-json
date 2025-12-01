"""
Simple GPU Detection Test
Tests the new robust GPU detection system
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gpu_detector import gpu_detector

print("GPU DETECTION TEST")
print("=" * 40)

# Test the new GPU detector
gpu_info = gpu_detector.detect_gpu(force_refresh=True)

print(f"PyTorch Available: {gpu_info['pytorch_available']}")
print(f"CUDA Available: {gpu_info['cuda_available']}")
print(f"GPU Count: {gpu_info['gpu_count']}")
print(f"Detection Method: {gpu_info['detection_method']}")

if gpu_info["gpus"]:
    print("\nDetected GPUs:")
    for gpu in gpu_info["gpus"]:
        print(f"  - {gpu.get('name', 'Unknown GPU')}")
        if gpu.get("memory_total"):
            print(f"    Memory: {gpu['memory_total'] / 1024**3:.1f} GB")
else:
    print("\nNo GPUs detected")

if gpu_info["system_gpus"]:
    print("\nSystem GPUs:")
    for gpu in gpu_info["system_gpus"]:
        print(f"  - {gpu.get('name', 'Unknown')}")

# Test GPU functionality
print(f"\nGPU Available for AI: {gpu_detector.is_gpu_available()}")
print(f"Recommended Device: {gpu_detector.get_device()}")

# Test memory allocation
test_result = gpu_detector.test_gpu_allocation()
if test_result["success"]:
    print("GPU Memory Test: PASSED")
else:
    print(f"GPU Memory Test: FAILED - {test_result['error']}")

if gpu_info["errors"]:
    print("\nErrors:")
    for error in gpu_info["errors"]:
        print(f"  - {error}")

print("\n" + "=" * 40)
print("Test completed successfully!")
