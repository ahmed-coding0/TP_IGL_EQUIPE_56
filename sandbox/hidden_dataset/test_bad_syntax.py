import pytest
from bad_syntax import calculate_sum
from typing import Union

@pytest.mark.parametrize(
    "args, expected_sum",
    [
        # --- Basic integer sums ---
        ((1, 2, 3), 6),
        ((10, -5, 2), 7),
        ((-1, -2, -3), -6),
        ((0, 0, 0), 0),
        ((5,), 5),  # Single integer argument
        ((100, 0, -100), 0),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 55), # More arguments

        # --- Basic float sums ---
        ((1.0, 2.0, 3.0), 6.0),
        ((10.5, -5.5, 2.0), 7.0),
        ((-1.1, -2.2, -3.3), -6.6),
        ((0.0, 0.0, 0.0), 0.0),
        ((5.5,), 5.5),  # Single float argument
        ((100.0, 0.0, -100.0), 0.0),
        ((0.1, 0.2, 0.3), 0.6), # Floats with potential precision issues (pytest.approx handles this)

        # --- Mixed integer and float sums (should return float) ---
        ((1, 2.0, 3), 6.0),
        ((10.5, -5, 2), 7.5),
        ((-1, -2.5, -3), -6.5),
        ((0, 0.0, 0), 0.0),
        ((5, 0.5), 5.5),
        ((10, 20.5, 30), 60.5),
        ((-10.5, 5, -2), -7.5),
    ]
)
def test_calculate_sum_valid_numeric_inputs(args: tuple[Union[int, float], ...], expected_sum: Union[int, float]):
    """
    Tests calculate_sum with various valid integer and float inputs,
    including mixed types, positive, negative, and zero values.
    Uses pytest.approx for robust float comparison.
    """
    result = calculate_sum(*args)
    assert result == pytest.approx(expected_sum)

def test_calculate_sum_empty_input():
    """
    Tests calculate_sum with no arguments, expecting a sum of 0 as per docstring.
    """
    result = calculate_sum()
    assert result == 0

@pytest.mark.parametrize(
    "args, expected_sum",
    [
        ((True,), 1),
        ((False,), 0),
        ((True, False, 5), 6),
        ((True, 2.5), 3.5),
        ((False, -10), -10),
        ((True, True, True), 3),
        ((False, False, False), 0),
        ((True, False, True, 10, 20.5), 32.5),
    ]
)
def test_calculate_sum_with_booleans(args: tuple[Union[int, float, bool], ...], expected_sum: Union[int, float]):
    """
    Tests calculate_sum with boolean inputs. Booleans are numeric (subclass of int)
    in Python and should be summed correctly (True as 1, False as 0).
    """
    result = calculate_sum(*args)
    assert result == pytest.approx(expected_sum)

@pytest.mark.parametrize(
    "args",
    [
        ("hello",),                 # Single string
        ([],),                      # Single empty list
        ({},),                      # Single empty dictionary
        (None,),                     # Single None
        ((1, "two", 3),),            # String mixed with numbers
        ((1, [2, 3], 4),),           # List mixed with numbers
        ((1, {"a": 1}, 2),),         # Dictionary mixed with numbers
        ((None, 1, 2),),             # None mixed with numbers
        ((1, 2, b"bytes"),),         # Bytes object
        ((1, 2, complex(1, 2)),),    # Complex number (sum() raises TypeError for complex)
        ((1, 2, (3, 4)),),           # Tuple mixed with numbers
    ]
)
def test_calculate_sum_invalid_non_numeric_inputs_raises_type_error(args: tuple):
    """
    Tests calculate_sum with non-numeric arguments, expecting a TypeError.
    The built-in sum() function naturally raises TypeError for non-numeric types
    that cannot be added.
    """
    with pytest.raises(TypeError):
        calculate_sum(*args)