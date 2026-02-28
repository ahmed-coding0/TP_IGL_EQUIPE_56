from typing import Union

def calculate_sum(*args: Union[int, float]) -> Union[int, float]:
    """
    Calculates the sum of all provided numeric arguments.

    This function accepts a variable number of arguments and returns their sum.
    It can handle both integers and floating-point numbers.

    Args:
        *args: A variable number of numeric arguments (int or float).

    Returns:
        Union[int, float]: The sum of all input numbers. The return type
                           will be float if any input is a float, otherwise int.
                           Returns 0 if no arguments are provided.

    Raises:
        TypeError: If any of the arguments are not numeric (e.g., string, list).
    """
    # The built-in sum() function correctly handles:
    # - An empty iterable (returns 0).
    # - Mixed int/float types (promotes to float if any float is present).
    # - Non-numeric types (raises a TypeError).
    return sum(args)