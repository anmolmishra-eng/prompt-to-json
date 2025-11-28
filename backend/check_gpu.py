"""
GPU Detection Script
Check what GPU hardware and drivers you have
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
            print("❌ CUDA not available")
    except ImportError:
        print("❌ PyTorch not installed")

    # Check Windows GPU info
    try:
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Get-WmiObject Win32_VideoController | Select-Object Name, DriverVersion | Format-Table -AutoSize",
            ],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            print("\n💻 Windows GPU Info:")
            print(result.stdout)
        else:
            print("❌ Could not get Windows GPU info")
    except Exception as e:
        print(f"❌ Error checking Windows GPU: {e}")

    # Check NVIDIA-SMI
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n🎮 NVIDIA-SMI Output:")
            print(result.stdout)
        else:
            print("❌ nvidia-smi not available or no permissions")
    except FileNotFoundError:
        print("❌ nvidia-smi not found - NVIDIA drivers not installed")

    # Recommendations
    print("\n💡 Recommendations:")
    if not torch.cuda.is_available():
        print("1. Install NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
        print("2. Make sure you have an NVIDIA GPU (not Intel/AMD)")
        print("3. Update NVIDIA drivers")
        print("4. Restart computer after installation")
    else:
        print("✅ GPU setup looks good!")


if __name__ == "__main__":
    check_gpu()
