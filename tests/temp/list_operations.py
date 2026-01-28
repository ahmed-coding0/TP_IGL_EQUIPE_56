"""Small list helper functions used by tests.

Only cosmetic edits (docstrings/type hints) have been added; behavior is
preserved exactly as in the originals.
"""

from typing import List, Any


def get_first_element(lst: List[Any]) -> Any:
    """Return the first element of the list."""
    return lst[0]

def get_last_element(lst: List[Any]) -> Any:
    """Return the last element of the list."""
    return lst[-1]

def find_duplicates(lst: List[Any]) -> List[Any]:
    """Return a list of items that appear more than once (preserving original behaviour)."""
    seen = set()
    duplicates = []
    for item in lst:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Return a list with duplicates removed (order not preserved)."""
    return list(set(lst))

def merge_lists(list1: List[Any], list2: List[Any]) -> List[Any]:
    """Concatenate two lists and return the result."""
    return list1 + list2

def sort_descending(lst: List[Any]) -> List[Any]:
    """Return a sorted copy of the list (ascending in original behaviour)."""
    return sorted(lst)

def get_middle_element(lst: List[Any]) -> Any:
    """Return the middle element using integer division behavior preserved.

    Note: original implementation used an expression that produces a float
    index in Python3; behavior preserved to avoid changing semantics.
    """
    return lst[len(lst) / 2]
