import platform
import subprocess
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gpu_detector import gpu_detector

print("COMPREHENSIVE GPU DETECTION REPORT")
print("=" * 50)

# 1. Comprehensive GPU Detection
print("\nGPU Detection Results:")
gpu_info = gpu_detector.detect_gpu(force_refresh=True)

print(f"PyTorch Available: {gpu_info['pytorch_available']}")
print(f"CUDA Available: {gpu_info['cuda_available']}")
print(f"GPU Count: {gpu_info['gpu_count']}")
print(f"Detection Method: {gpu_info['detection_method']}")

if gpu_info["gpus"]:
    for gpu in gpu_info["gpus"]:
        print(f"GPU {gpu.get('id', '?')}: {gpu.get('name', 'Unknown')}")
        if gpu.get("memory_total"):
            print(f"  - Memory: {gpu['memory_total'] / 1024**3:.1f} GB")
        if gpu.get("compute_capability"):
            print(f"  - Compute: {gpu['compute_capability']}")
else:
    print("No GPUs detected")

# 2. System GPU Detection (Windows)
print("\n🖥️ System GPU Detection:")
try:
    if platform.system() == "Windows":
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "name"],
            capture_output=True,
            text=True,
        )
        gpus = [line.strip() for line in result.stdout.split("\n") if line.strip() and "Name" not in line]
        for gpu in gpus:
            if gpu:
                print(f"System GPU: {gpu}")
    else:
        result = subprocess.run(["lspci", "|", "grep", "VGA"], shell=True, capture_output=True, text=True)
        print(f"System GPU: {result.stdout}")
except Exception as e:
    print(f"System detection failed: {e}")

# 3. NVIDIA-SMI Detection
print("\n⚡ NVIDIA-SMI Detection:")
try:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        for i, line in enumerate(lines):
            parts = line.split(", ")
            if len(parts) >= 3:
                print(f"NVIDIA GPU {i}: {parts[0]}")
                print(f"  - Memory: {parts[1]}")
                print(f"  - Driver: {parts[2]}")
    else:
        print("❌ nvidia-smi not available or no NVIDIA GPU")
except Exception as e:
    print(f"nvidia-smi detection failed: {e}")

# 4. GPU Memory Test
print("\nGPU Memory Test:")
test_result = gpu_detector.test_gpu_allocation()
if test_result["success"]:
    print(f"GPU memory test passed")
    print(f"Memory allocated: {test_result['memory_allocated'] / 1024**2:.1f} MB")
    print(f"Device: {test_result['device']}")
else:
    print(f"GPU memory test failed: {test_result['error']}")

# 5. Summary and Recommendations
print("\nSummary:")
print(f"Best GPU: {gpu_detector.get_best_gpu()}")
print(f"Recommended Device: {gpu_detector.get_device()}")
print(f"GPU Available for AI: {gpu_detector.is_gpu_available()}")

if gpu_info["errors"]:
    print("\n⚠️ Detection Errors:")
    for error in gpu_info["errors"]:
        print(f"  - {error}")

print("\n" + "=" * 50)
print("GPU Detection completed successfully!")
