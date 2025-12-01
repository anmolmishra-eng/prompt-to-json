"""
GPU Detection Fix Script
Addresses inconsistent GPU detection issues
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gpu_detector import gpu_detector


def diagnose_gpu_issues():
    """Diagnose and fix GPU detection issues"""
    print("🔧 GPU Detection Diagnostic Tool")
    print("=" * 50)

    # Run comprehensive detection
    gpu_info = gpu_detector.detect_gpu(force_refresh=True)

    print("\n📊 Detection Results:")
    print(f"PyTorch Available: {gpu_info['pytorch_available']}")
    print(f"CUDA Available: {gpu_info['cuda_available']}")
    print(f"GPU Count: {gpu_info['gpu_count']}")
    print(f"Detection Method: {gpu_info['detection_method']}")

    # Identify issues
    issues = []
    fixes = []

    if not gpu_info["pytorch_available"]:
        issues.append("PyTorch not installed")
        fixes.append("Install PyTorch: pip install torch torchvision torchaudio")

    if gpu_info["pytorch_available"] and not gpu_info["cuda_available"]:
        issues.append("CUDA not available in PyTorch")
        fixes.append(
            "Install CUDA-enabled PyTorch: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        )

    if not gpu_info["system_gpus"] and not gpu_info["gpus"]:
        issues.append("No GPUs detected by any method")
        fixes.append("Check if NVIDIA GPU is properly installed and drivers are updated")

    if gpu_info["errors"]:
        for error in gpu_info["errors"]:
            issues.append(f"Detection error: {error}")

    # Report issues
    if issues:
        print("\n⚠️ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print("\n🔧 Recommended Fixes:")
        for i, fix in enumerate(fixes, 1):
            print(f"  {i}. {fix}")
    else:
        print("\n✅ No issues detected - GPU detection is working correctly!")

    # Test GPU functionality
    print("\n🧪 Testing GPU Functionality:")
    test_result = gpu_detector.test_gpu_allocation()

    if test_result["success"]:
        print("✅ GPU memory allocation test passed")
        print(f"   Device: {test_result['device']}")
        print(f"   Memory: {test_result['memory_allocated'] / 1024**2:.1f} MB")
    else:
        print(f"❌ GPU memory allocation test failed: {test_result['error']}")

    # Provide device recommendation
    print(f"\n🎯 Recommended Device for AI Processing: {gpu_detector.get_device()}")

    return len(issues) == 0


if __name__ == "__main__":
    success = diagnose_gpu_issues()

    print("\n" + "=" * 50)
    if success:
        print("🎉 GPU detection is working correctly!")
    else:
        print("⚠️ GPU detection issues found - follow the recommended fixes above")
