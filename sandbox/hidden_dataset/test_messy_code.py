import pytest
from messy_code import f

# Test cases for values strictly within the range (0, 100)
@pytest.mark.parametrize("z_value", [
    1,
    50,
    99,
    0.001,  # Float just above 0
    50.0,   # Float in middle
    99.999  # Float just below 100
])
def test_f_returns_true_for_in_range_values(z_value):
    """
    Tests that f returns True for integer and float values strictly between 0 and 100.
    """
    assert f(z_value) is True

# Test cases for values outside or at the boundaries of the range (0, 100)
@pytest.mark.parametrize("z_value", [
    0,      # Lower boundary (exclusive)
    100,    # Upper boundary (exclusive)
    -1,     # Below lower boundary
    -100,   # Significantly below lower boundary
    101,    # Above upper boundary
    200,    # Significantly above upper boundary
    0.0,    # Float at lower boundary
    -0.001, # Float just below 0
    100.0,  # Float at upper boundary
    100.001 # Float just above 100
])
def test_f_returns_false_for_out_of_range_values(z_value):
    """
    Tests that f returns False for integer and float values outside or at the boundaries of (0, 100).
    """
    assert f(z_value) is False

# Test cases for boolean inputs (which are subclasses of int)
def test_f_with_boolean_true():
    """
    Tests f with True (equivalent to 1), which should be in range.
    """
    assert f(True) is True

def test_f_with_boolean_false():
    """
    Tests f with False (equivalent to 0), which should be out of range.
    """
    assert f(False) is False

# Test cases for non-comparable types that should raise TypeError
@pytest.mark.parametrize("z_value, expected_type_name", [
    ("hello", "str"),
    ([1, 2], "list"),
    ({"key": "value"}, "dict"),
    (None, "NoneType"),
    (object(), "object"),
    (frozenset(), "frozenset"),
    (complex(1, 2), "complex") # Complex numbers are not comparable with <, >
])
def test_f_raises_type_error_for_non_comparable_types(z_value, expected_type_name):
    """
    Tests that f raises a TypeError with a specific message for non-comparable input types.
    Also checks that the original TypeError is chained.
    """
    with pytest.raises(TypeError) as excinfo:
        f(z_value)
    
    # Check the custom error message content
    expected_message_part = (
        f"Input 'z' must be an integer or a comparable numeric type for this check. "
        f"Got {expected_type_name}."
    )
    assert expected_message_part in str(excinfo.value)
    
    # Ensure the original TypeError is chained as per the implementation
    assert excinfo.value.__cause__ is not None
    assert isinstance(excinfo.value.__cause__, TypeError)

# Additional edge case for large numbers to ensure no overflow or unexpected behavior
def test_f_with_very_large_integer_out_of_range():
    """
    Tests f with a very large integer far outside the range.
    """
    assert f(1_000_000_000) is False

def test_f_with_very_small_integer_out_of_range():
    """
    Tests f with a very small (negative) integer far outside the range.
    """
    assert f(-1_000_000_000) is False