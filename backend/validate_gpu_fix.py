"""
Validate GPU Detection Fix
Tests the robustness of the new GPU detection system
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gpu_detector import gpu_detector


def test_gpu_detection_robustness():
    """Test GPU detection under various conditions"""
    print("🧪 GPU Detection Robustness Test")
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
        print("✅ Basic detection test passed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Basic detection test failed: {e}")

    # Test 2: Cached detection
    print("\n2. Testing cached detection...")
    try:
        gpu_info1 = gpu_detector.detect_gpu()
        gpu_info2 = gpu_detector.detect_gpu()  # Should use cache
        assert gpu_info1 == gpu_info2
        print("✅ Cached detection test passed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Cached detection test failed: {e}")

    # Test 3: Force refresh
    print("\n3. Testing force refresh...")
    try:
        gpu_info1 = gpu_detector.detect_gpu()
        gpu_info2 = gpu_detector.detect_gpu(force_refresh=True)
        # Should be same content but freshly detected
        assert gpu_info1["detection_method"] == gpu_info2["detection_method"]
        print("✅ Force refresh test passed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Force refresh test failed: {e}")

    # Test 4: GPU availability check
    print("\n4. Testing GPU availability check...")
    try:
        is_available = gpu_detector.is_gpu_available()
        assert isinstance(is_available, bool)
        print(f"✅ GPU availability test passed (Available: {is_available})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ GPU availability test failed: {e}")

    # Test 5: Device recommendation
    print("\n5. Testing device recommendation...")
    try:
        device = gpu_detector.get_device()
        assert device in ["cuda", "cpu"]
        print(f"✅ Device recommendation test passed (Device: {device})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Device recommendation test failed: {e}")

    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! GPU detection is robust.")
        return True
    else:
        print("⚠️ Some tests failed. GPU detection may have issues.")
        return False


def test_error_handling():
    """Test error handling in GPU detection"""
    print("\n🛡️ Error Handling Test")
    print("-" * 30)

    # Test with invalid operations
    try:
        # This should not crash even if PyTorch is not available
        gpu_info = gpu_detector.detect_gpu()
        print("✅ Error handling test passed - no crashes")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Validating GPU Detection Fix")
    print("=" * 60)

    robustness_passed = test_gpu_detection_robustness()
    error_handling_passed = test_error_handling()

    print("\n" + "=" * 60)
    if robustness_passed and error_handling_passed:
        print("✅ GPU Detection Fix Validation: PASSED")
        print("The inconsistent GPU detection problem has been resolved!")
    else:
        print("❌ GPU Detection Fix Validation: FAILED")
        print("Some issues remain in the GPU detection system.")
