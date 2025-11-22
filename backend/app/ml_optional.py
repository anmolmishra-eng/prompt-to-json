"""
Optional ML imports with fallbacks for CI environments
"""

try:
    import torch
    import transformers

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

    # Mock classes for CI
    class MockTorch:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    torch = MockTorch()
    transformers = MockTorch()


def get_ml_status():
    return ML_AVAILABLE
