"""
Spec JSON Validator - Strict validation before geometry generation
Prevents silent fallbacks by validating spec completeness
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SpecValidationError(Exception):
    """Raised when spec_json is incomplete or invalid"""

    pass


def validate_spec_json(spec_json: Dict) -> None:
    """
    Strict validation of spec_json before geometry generation
    Raises SpecValidationError if spec is incomplete
    """
    errors = []

    # 1. Required top-level keys
    required_keys = ["design_type", "dimensions"]
    for key in required_keys:
        if key not in spec_json:
            errors.append(f"Missing required key: '{key}'")

    if errors:
        raise SpecValidationError("; ".join(errors))

    # 2. Validate dimensions
    dimensions = spec_json.get("dimensions", {})
    if not isinstance(dimensions, dict):
        raise SpecValidationError(f"'dimensions' must be a dict, got {type(dimensions).__name__}")

    required_dims = ["width", "length", "height"]
    for dim in required_dims:
        if dim not in dimensions:
            errors.append(f"Missing dimension: '{dim}'")
        elif dimensions[dim] is None:
            errors.append(f"Dimension '{dim}' is null")
        elif not isinstance(dimensions[dim], (int, float)):
            errors.append(f"Dimension '{dim}' must be numeric, got {type(dimensions[dim]).__name__}")
        elif dimensions[dim] <= 0:
            errors.append(f"Dimension '{dim}' must be positive, got {dimensions[dim]}")

    if errors:
        raise SpecValidationError("; ".join(errors))

    # 3. Validate design_type
    design_type = spec_json.get("design_type")
    if not design_type or not isinstance(design_type, str):
        raise SpecValidationError(f"'design_type' must be a non-empty string")

    # 4. Validate objects (if present)
    if "objects" in spec_json:
        objects = spec_json["objects"]
        if not isinstance(objects, list):
            raise SpecValidationError(f"'objects' must be a list, got {type(objects).__name__}")

    logger.info(
        f"Spec validation passed: {design_type} ({dimensions['width']}x{dimensions['length']}x{dimensions['height']}m)"
    )


def validate_with_warnings(spec_json: Dict) -> List[str]:
    """
    Validate spec and return warnings for missing optional fields
    Does not raise errors, only logs warnings
    """
    warnings = []

    # Check optional fields
    if "objects" not in spec_json or not spec_json["objects"]:
        warnings.append("No objects defined, will generate basic structure only")

    if "stories" not in spec_json:
        warnings.append("'stories' not specified, defaulting to 1")

    if "metadata" not in spec_json:
        warnings.append("No metadata provided")

    # Log all warnings
    for warning in warnings:
        logger.warning(f"Spec validation warning: {warning}")

    return warnings
