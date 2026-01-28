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

2. **Functional Correctness Tests**: Generate tests based on semantic intent
   - If function is named `calculate_average`, test that it returns mean (not sum)
   - If function is named `get_user_by_name`, test it returns correct user
   - If function is named `validate_email`, test it validates properly

3. **Edge Cases**: Test all corner cases
   - Empty inputs ([], "", None)
   - Zero values
   - Negative values
   - Boundary conditions
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
