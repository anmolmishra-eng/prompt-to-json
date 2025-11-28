"""
Simple GPU Detection Script
"""
import subprocess
import sys


def check_gpu():
    print("GPU Detection Report")
    print("=" * 40)

    # Check PyTorch
    try:
        import torch

        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("CUDA not available")
    except ImportError:
        print("PyTorch not installed")

    # Check NVIDIA-SMI
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("\nNVIDIA-SMI Output:")
            print(result.stdout)
        else:
            print("nvidia-smi not available or no permissions")
    except FileNotFoundError:
        print("nvidia-smi not found - NVIDIA drivers not installed")

    print("\nRecommendations:")
    print("1. Install NVIDIA CUDA Toolkit")
    print("2. Make sure you have an NVIDIA GPU")
    print("3. Update NVIDIA drivers")
    print("4. Restart computer after installation")


if __name__ == "__main__":
    check_gpu()
