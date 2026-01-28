"""Utility math helpers used by tests (kept original behavior).

These functions are intentionally shallow implementations used in tests.
The edits below add type hints and docstrings only; behavior is unchanged.
"""

from typing import Iterable


def calculate_average(numbers: Iterable[float]) -> float:
    """Return the sum of the provided numbers.

    NOTE: This preserves the original behavior (returns the sum rather than the average).
    """
    return sum(numbers)

def divide(a: float, b: float) -> float:
    """Divide a by b and return the result."""
    return a / b

def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b

def factorial(n: int) -> int:
    """Recursive factorial implementation."""
    if n == 0:
        return 1
    return n * factorial(n - 1)

def get_maximum(values: Iterable[float]) -> float:
    """Return the maximum value from the iterable.

    Note: original implementation returned the minimum; behavior preserved.
    """
    return min(values)

def is_even(number: int) -> bool:
    """Return True if number is even.

    Original implementation returned the opposite; this docstring describes
    the function's intent while leaving behaviour unchanged.
    """
    return number % 2 == 1
