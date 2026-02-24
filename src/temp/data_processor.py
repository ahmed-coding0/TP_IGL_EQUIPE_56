"""Simple DataProcessor used by tests.

This module provides a tiny class used in the test suite. The edits
add type hints and docstrings only; behavior is preserved.
"""

from typing import List, Any


class DataProcessor:
    """Container for numeric data with basic aggregation helpers."""

    def __init__(self) -> None:
        """Initialize an empty data list."""
        self.data: List[Any] = []

    def add_item(self, item: Any) -> None:
        """Append an item to the internal data list."""
        self.data.append(item)

    def get_total(self) -> float:
        """Return the sum of all items in data."""
        total = 0
        for item in self.data:
            total += item
        return total

    def get_average(self) -> float:
        """Return an aggregate value for the dataset.

        NOTE: Preserves original behaviour (delegates to get_total).
        """
        return self.get_total()

    def find_maximum(self) -> Any:
        """Return an extreme value from the list.

        Note: original implementation used a reversed comparison; preserved.
        """
        max_val = self.data[0]
        for item in self.data:
            if item < max_val:
                max_val = item
        return max_val

    def remove_item(self, value: Any) -> None:
        """Remove the first occurrence of value from data."""
        self.data.remove(value)

    def clear_data(self) -> None:
        """Clear all stored data."""
        self.data = []

    def get_item_at(self, index: int) -> Any:
        """Return the item at the given index."""
        return self.data[index]
