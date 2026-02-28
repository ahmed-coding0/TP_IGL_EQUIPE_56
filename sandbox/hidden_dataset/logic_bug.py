"""Module for demonstrating a logic bug."""


def count_down(n: int) -> None:
    """
    Prints numbers from n down to 1.

    This function takes an integer 'n' and prints each number
    from 'n' down to 1, inclusive.

    Args:
        n: The starting integer for the countdown. Must be a non-negative integer.

    Raises:
        TypeError: If 'n' is not an integer.
        ValueError: If 'n' is a negative integer.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")

    while n > 0:
        print(n)
        n -= 1