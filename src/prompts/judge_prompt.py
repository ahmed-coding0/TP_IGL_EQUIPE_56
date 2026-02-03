"""Judge Agent Prompt Configuration."""


def create_test_generation_prompt(file_path: str, code: str, issues: str) -> str:
    """
    Create a prompt for the Judge agent to generate pytest tests.
    
    Args:
        file_path: Path to the file being tested
        code: The code to generate tests for
        issues: Issues found by the Auditor (to create tests that expose bugs)
        
    Returns:
        Complete prompt string for test generation
    """
    # Extract just the filename without path
    from pathlib import Path
    module_name = Path(file_path).stem  # e.g., "user_manager" from "user_manager.py"
    
    prompt = f"""Generate comprehensive pytest tests for the following Python code.

FILE PATH: {file_path}
MODULE NAME: {module_name}

CODE TO TEST:
```python
{code}
```

KNOWN ISSUES (Create tests that expose these):
{issues}

CRITICAL REQUIREMENTS:

1. **Import Statement**: Use simple import, NOT relative paths:
   ```python
   from {module_name} import ClassName  # CORRECT
   # NOT: from .path.to.{module_name} import ClassName  # WRONG
   ```

2. **Functional Correctness Tests** (CRITICAL - READ CAREFULLY):
   **YOU MUST TEST SEMANTIC INTENT, NOT CURRENT IMPLEMENTATION**
   
   **WRONG APPROACH** (testing buggy behavior):
   ```python
   # If code has: def calculate_average(nums): return sum(nums)
   def test_average():
       assert calculate_average([10, 20]) == 30  # Tests the BUG!
   ```
   
   **CORRECT APPROACH** (testing intended behavior):
   ```python
   # Test what "average" SHOULD mean (arithmetic mean)
   def test_average():
       assert calculate_average([10, 20]) == 15.0  # sum/length = 30/2 = 15
       assert calculate_average([5, 10, 15]) == 10.0  # 30/3 = 10
       assert calculate_average([100]) == 100.0  # 100/1 = 100
   ```
   
   **Function Name → Expected Behavior Mapping**:
   - `calculate_average` → return sum/length (arithmetic mean)
   - `get_maximum` → return max(a, b), not min(a, b)
   - `is_even` → return n % 2 == 0, not n % 2 == 1
   - `find_user_by_name` → return user with matching name
   - `validate_email` → return True if valid format
   - `calculate_factorial` → return n! (n * (n-1) * ... * 1)
   - `reverse_string` → return string[::-1]
   
   **CRITICAL RULE**: Analyze the function NAME and parameters to understand
   what it SHOULD do, then write tests for that behavior, even if the current
   code is buggy. Your tests will expose the bugs!

3. **Edge Cases**: Test boundary conditions
   - Empty inputs: [], "", None, {{}}
   - Zero and negative numbers
   - Single element collections
   - Invalid types

4. **Pytest Fixtures**: Use unique parameter names in fixtures
   ```python
   def test_function(list1, list2):  # CORRECT - unique names
   def test_function(list1, list1):  # WRONG - duplicate names
   ```

5. **Syntax Validation**: Ensure all tests are syntactically valid
   - No duplicate parameter names
   - Proper indentation
   - Valid pytest syntax

6. **Test Structure**: Each test should:
   - Have descriptive name
   - Test one specific behavior  
   - Use appropriate assertions
   - Handle expected exceptions with pytest.raises()
   - Invalid types

4. **Error Handling**: Test expected exceptions
   ```python
   with pytest.raises(ValueError, match="error message"):
       function_call()
   ```

5. **Test Coverage**: Aim for 100% code coverage
   - All functions
   - All branches (if/else)
   - All error paths

6. **Fixtures**: Use pytest fixtures for setup
   ```python
   @pytest.fixture
   def instance():
       return ClassName()
   ```

EXAMPLE OUTPUT FORMAT:
```python
import pytest
from {module_name} import ClassName

@pytest.fixture
def instance():
    return ClassName()

def test_method_valid_input(instance):
    \"\"\"Test with valid input.\"\"\"
    result = instance.method(valid_input)
    assert result == expected_value

def test_method_empty_input(instance):
    \"\"\"Test with empty input raises error.\"\"\"
    with pytest.raises(ValueError):
        instance.method([])
```

Return ONLY the complete test file code in ```python blocks. No explanations."""
    
    return prompt
