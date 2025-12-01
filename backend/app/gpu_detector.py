"""
Robust GPU Detection Module
Addresses inconsistent GPU detection for local AI processing
"""
import logging
import platform
import subprocess
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GPUDetector:
    """Comprehensive GPU detection with fallback mechanisms"""

    def __init__(self):
        self._gpu_info = None
        self._detection_cache = {}

    def detect_gpu(self, force_refresh: bool = False) -> Dict:
        """Main GPU detection with caching"""
        if self._gpu_info is not None and not force_refresh:
            return self._gpu_info

        detection_result = {
            "pytorch_available": False,
            "cuda_available": False,
            "gpu_count": 0,
            "gpus": [],
            "system_gpus": [],
            "nvidia_driver": None,
            "detection_method": "unknown",
            "errors": [],
        }

        # Method 1: PyTorch Detection (Primary)
        pytorch_result = self._detect_pytorch()
        detection_result.update(pytorch_result)

        # Method 2: System GPU Detection (Secondary)
        system_result = self._detect_system_gpu()
        detection_result["system_gpus"] = system_result

        # Method 3: NVIDIA-SMI Detection (Tertiary)
        nvidia_result = self._detect_nvidia_smi()
        if nvidia_result:
            detection_result["nvidia_driver"] = nvidia_result.get("driver_version")
            if not detection_result["gpus"]:
                detection_result["gpus"] = nvidia_result.get("gpus", [])
                detection_result["gpu_count"] = len(detection_result["gpus"])

        # Determine best detection method
        if detection_result["pytorch_available"] and detection_result["cuda_available"]:
            detection_result["detection_method"] = "pytorch_cuda"
        elif detection_result["system_gpus"]:
            detection_result["detection_method"] = "system_detection"
        elif nvidia_result:
            detection_result["detection_method"] = "nvidia_smi"
        else:
            detection_result["detection_method"] = "none"

        self._gpu_info = detection_result
        return detection_result

    def _detect_pytorch(self) -> Dict:
        """Detect GPU via PyTorch"""
        result = {"pytorch_available": False, "cuda_available": False, "gpu_count": 0, "gpus": []}

        try:
            import torch

            result["pytorch_available"] = True

            if torch.cuda.is_available():
                result["cuda_available"] = True
                result["gpu_count"] = torch.cuda.device_count()

                for i in range(torch.cuda.device_count()):
                    try:
                        gpu_info = {
                            "id": i,
                            "name": torch.cuda.get_device_name(i),
                            "memory_total": None,
                            "compute_capability": None,
                        }

                        # Get device properties
                        props = torch.cuda.get_device_properties(i)
                        gpu_info["memory_total"] = props.total_memory
                        gpu_info["compute_capability"] = f"{props.major}.{props.minor}"

                        result["gpus"].append(gpu_info)
                    except Exception as e:
                        logger.warning(f"Failed to get GPU {i} properties: {e}")
                        result["gpus"].append({"id": i, "name": f"GPU {i} (properties unavailable)", "error": str(e)})

        except ImportError:
            result["errors"] = ["PyTorch not installed"]
        except Exception as e:
            result["errors"] = [f"PyTorch detection failed: {str(e)}"]

        return result

    def _detect_system_gpu(self) -> List[Dict]:
        """Detect GPU via system commands"""
        gpus = []

        try:
            if platform.system() == "Windows":
                gpus = self._detect_windows_gpu()
            else:
                gpus = self._detect_linux_gpu()
        except Exception as e:
            logger.warning(f"System GPU detection failed: {e}")

        return gpus

    def _detect_windows_gpu(self) -> List[Dict]:
        """Windows GPU detection"""
        gpus = []

        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name,driverversion"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    line = line.strip()
                    if line and "Name" not in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            gpus.append(
                                {"name": " ".join(parts[:-1]), "driver_version": parts[-1], "source": "windows_wmic"}
                            )
        except Exception as e:
            logger.warning(f"Windows GPU detection failed: {e}")

        return gpus

    def _detect_linux_gpu(self) -> List[Dict]:
        """Linux GPU detection"""
        gpus = []

        try:
            result = subprocess.run(["lspci", "-nn"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line or "Display" in line:
                        gpus.append({"name": line.strip(), "source": "linux_lspci"})
        except Exception as e:
            logger.warning(f"Linux GPU detection failed: {e}")

        return gpus

    def _detect_nvidia_smi(self) -> Optional[Dict]:
        """NVIDIA-SMI detection"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                gpus = []
                lines = result.stdout.strip().split("\n")

                for i, line in enumerate(lines):
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 3:
                        gpus.append(
                            {
                                "id": i,
                                "name": parts[0],
                                "memory_total": int(parts[1]) * 1024 * 1024,  # Convert MB to bytes
                                "source": "nvidia_smi",
                            }
                        )

                return {"gpus": gpus, "driver_version": parts[2] if parts else None}

        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.info("nvidia-smi not available")
        except Exception as e:
            logger.warning(f"nvidia-smi detection failed: {e}")

        return None

    def is_gpu_available(self) -> bool:
        """Quick check if GPU is available for AI processing"""
        info = self.detect_gpu()
        return info["cuda_available"] and info["gpu_count"] > 0

    def get_best_gpu(self) -> Optional[Dict]:
        """Get the best available GPU for AI processing"""
        info = self.detect_gpu()

        if not info["gpus"]:
            return None

        # Prefer GPU with most memory
        best_gpu = max(info["gpus"], key=lambda g: g.get("memory_total", 0))
        return best_gpu

    def test_gpu_allocation(self) -> Dict:
        """Test GPU memory allocation"""
        if not self.is_gpu_available():
            return {"success": False, "error": "No GPU available"}

        try:
            import torch

            device = torch.device("cuda:0")

            # Test small allocation
            test_tensor = torch.randn(100, 100).to(device)
            memory_allocated = torch.cuda.memory_allocated(0)

            # Cleanup
            del test_tensor
            torch.cuda.empty_cache()

            return {"success": True, "memory_allocated": memory_allocated, "device": str(device)}

        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
gpu_detector = GPUDetector()


def get_gpu_info(force_refresh: bool = False) -> Dict:
    """Get comprehensive GPU information"""
    return gpu_detector.detect_gpu(force_refresh)


def is_gpu_available() -> bool:
    """Quick GPU availability check"""
    return gpu_detector.is_gpu_available()


def get_device() -> str:
    """Get the best device for AI processing"""
    return "cuda" if is_gpu_available() else "cpu"


# Add method to GPUDetector class
GPUDetector.get_device = lambda self: "cuda" if self.is_gpu_available() else "cpu"
