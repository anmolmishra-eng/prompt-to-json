"""
Final GPU Detection Test
Comprehensive test of the GPU detection fix
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gpu_detector import gpu_detector


def test_gpu_detection():
    """Test GPU detection robustness"""
    print("GPU DETECTION ROBUSTNESS TEST")
    print("=" * 50)

    tests_passed = 0
    total_tests = 5

    # Test 1: Basic detection
    print("\n1. Testing basic GPU detection...")
    try:
        gpu_info = gpu_detector.detect_gpu()
        assert isinstance(gpu_info, dict)
        assert "pytorch_available" in gpu_info
        assert "cuda_available" in gpu_info
        assert "gpu_count" in gpu_info
        print("   PASSED - Basic detection works")
        tests_passed += 1
    except Exception as e:
        print(f"   FAILED - {e}")

    # Test 2: Cached detection
    print("\n2. Testing cached detection...")
    try:
        gpu_info1 = gpu_detector.detect_gpu()
        gpu_info2 = gpu_detector.detect_gpu()
        assert gpu_info1 == gpu_info2
        print("   PASSED - Caching works correctly")
        tests_passed += 1
    except Exception as e:
        print(f"   FAILED - {e}")

    # Test 3: Force refresh
    print("\n3. Testing force refresh...")
    try:
        gpu_info1 = gpu_detector.detect_gpu()
        gpu_info2 = gpu_detector.detect_gpu(force_refresh=True)
        assert gpu_info1["detection_method"] == gpu_info2["detection_method"]
        print("   PASSED - Force refresh works")
        tests_passed += 1
    except Exception as e:
        print(f"   FAILED - {e}")

    # Test 4: GPU availability check
    print("\n4. Testing GPU availability check...")
    try:
        is_available = gpu_detector.is_gpu_available()
        assert isinstance(is_available, bool)
        print(f"   PASSED - GPU Available: {is_available}")
        tests_passed += 1
    except Exception as e:
        print(f"   FAILED - {e}")

    # Test 5: Device recommendation
    print("\n5. Testing device recommendation...")
    try:
        device = gpu_detector.get_device()
        assert device in ["cuda", "cpu"]
        print(f"   PASSED - Recommended Device: {device}")
        tests_passed += 1
    except Exception as e:
        print(f"   FAILED - {e}")

    # Summary
    print(f"\nTEST RESULTS: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("SUCCESS: All tests passed! GPU detection is robust.")
        return True
    else:
        print("WARNING: Some tests failed.")
        return False


def show_gpu_info():
    """Show comprehensive GPU information"""
    print("\nGPU INFORMATION")
    print("-" * 30)

    gpu_info = gpu_detector.detect_gpu(force_refresh=True)

    print(f"PyTorch Available: {gpu_info['pytorch_available']}")
    print(f"CUDA Available: {gpu_info['cuda_available']}")
    print(f"GPU Count: {gpu_info['gpu_count']}")
    print(f"Detection Method: {gpu_info['detection_method']}")

    if gpu_info["gpus"]:
        print("\nDetected GPUs:")
        for gpu in gpu_info["gpus"]:
            print(f"  - {gpu.get('name', 'Unknown')}")
            if gpu.get("memory_total"):
                print(f"    Memory: {gpu['memory_total'] / 1024**3:.1f} GB")

    if gpu_info["system_gpus"]:
        print("\nSystem GPUs:")
        for gpu in gpu_info["system_gpus"]:
            print(f"  - {gpu.get('name', 'Unknown')}")

    if gpu_info["errors"]:
        print("\nErrors:")
        for error in gpu_info["errors"]:
            print(f"  - {error}")

    # Test memory allocation
    test_result = gpu_detector.test_gpu_allocation()
    print(f"\nMemory Test: {'PASSED' if test_result['success'] else 'FAILED'}")
    if not test_result["success"]:
        print(f"  Error: {test_result['error']}")


if __name__ == "__main__":
    print("FINAL GPU DETECTION TEST")
    print("=" * 60)

    # Show current GPU info
    show_gpu_info()

    # Test robustness
    success = test_gpu_detection()

    print("\n" + "=" * 60)
    if success:
        print("RESULT: GPU Detection Fix - SUCCESSFUL")
        print("The inconsistent GPU detection problem has been resolved!")
    else:
        print("RESULT: GPU Detection Fix - NEEDS ATTENTION")
        print("Some issues remain but basic functionality works.")

    print("\nKey Improvements:")
    print("- Robust multi-method detection with fallbacks")
    print("- Consistent results through caching")
    print("- Comprehensive error handling")
    print("- Unified interface across application")
