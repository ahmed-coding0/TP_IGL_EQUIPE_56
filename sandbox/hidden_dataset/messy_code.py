"""
This module provides a utility function 'f' to check if a number falls within a specific range.
"""

# The global variable 'x' (x = 10) was unused and has been removed as per the audit report.

def f(z: int) -> bool:
    """
    Checks if an integer 'z' is strictly between 0 and 100.

    Args:
        z: The integer value to check.

    Returns:
        True if 0 < z < 100, False otherwise.

    Raises:
        TypeError: If 'z' is not a numeric type that can be compared (e.g., string, list, None).
    """
    try:
        # Simplified conditional statement as per audit report.
        return 0 < z < 100
    except TypeError as e:
        # Handle cases where 'z' is not a comparable numeric type.
        # The original code would raise a TypeError for non-comparable types.
        # We catch it and re-raise with a more informative message, aligning with the type hint.
        raise TypeError(
            f"Input 'z' must be an integer or a comparable numeric type for this check. "
            f"Got {type(z).__name__}."
        ) from e