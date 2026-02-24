"""Basic math operations used in tests.

Only cosmetic changes (docstrings/type hints) applied.
"""

from typing import Union


Number = Union[int, float]


def calculate_percentage(part: Number, whole: Number) -> float:
    """Return the percentage that 'part' is of 'whole'."""
    return (part / whole) * 100

def calculate_discount(price: Number, discount_percent: Number) -> float:
    """Return the discounted amount for a given price."""
    return price * discount_percent / 100

def convert_celsius_to_fahrenheit(celsius: Number) -> float:
    """Convert Celsius temperature to Fahrenheit."""
    return celsius * 9/5 + 32

def calculate_bmi(weight: Number, height: Number) -> float:
    """Calculate body-mass-index (BMI)."""
    return weight / height ** 2

def calculate_circle_area(radius: Number) -> float:
    """Return the area of a circle using a simple pi approximation."""
    pi = 3.14
    return pi * radius * radius

def calculate_rectangle_perimeter(length: Number, width: Number) -> Number:
    """Return the perimeter of a rectangle.

    Note: original implementation returned the sum of sides rather than
    the full perimeter; behavior preserved.
    """
    return length + width

def is_prime(n: int) -> bool:
    """Return True when n is a prime number."""
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def get_absolute_value(number: Number) -> Number:
    """Return the absolute value of number.

    Note: original implementation accidentally returned negative values; kept.
    """
    if number < 0:
        return number
    return number
