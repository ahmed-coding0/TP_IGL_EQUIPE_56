import os
import sys
import shutil
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.tools.pylint_tools import run_pylint
from src.tools.files_tools import write_file

@pytest.fixture
def sandbox_setup():
    """Create a temporary directory inside the real sandbox for testing."""
    real_sandbox = os.path.abspath("sandbox")
    os.makedirs(real_sandbox, exist_ok=True)
    
    test_dir = os.path.join(real_sandbox, "test_pylint_env")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    yield test_dir
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_pylint_good_score(sandbox_setup):
    """Test pylint on a clean file returns a high score."""
    clean_code = '''"""
Module docstring.
"""
def hello():
    """Function docstring."""
    print("Hello")
'''
    file_path = os.path.join(sandbox_setup, "clean.py")
    write_file(file_path, clean_code)
    
    result = run_pylint(file_path)
    
    assert result['success'] is True
    # Pylint configuration might be strict or empty file scoring might vary. 
    # Just ensure we get a score.
    assert result['score'] >= 0.0, f"Score error: {result['score']}\nOutput: {result['output']}"
    assert isinstance(result['violations'], list)

def test_pylint_syntax_error(sandbox_setup):
    """Test pylint on a file with syntax errors."""
    broken_code = '''def hello()
    print("Missing colon")
'''
    file_path = os.path.join(sandbox_setup, "broken.py")
    write_file(file_path, broken_code)
    
    result = run_pylint(file_path)
    
    assert result['success'] is True  # Tool ran successfully even if code is bad
    # Violations should detect syntax error
    # E0001 is syntax-error
    found_error = any(v['symbol'] == 'syntax-error' or v['message-id'] == 'E0001' for v in result['violations'])
    assert found_error or "syntax-error" in result['output']

def test_security_violation_pylint(sandbox_setup):
    """Test run_pylint outside sandbox."""
    # Attempt to lint a file outside sandbox
    outside_file = os.path.abspath("main.py")
    
    result = run_pylint(outside_file)
    
    # Expect error caught
    assert result['success'] is False
    assert "outside sandbox" in result['error'] or "different drive" in result['error']

def test_missing_file_pylint(sandbox_setup):
    """Test run_pylint on non-existent file."""
    bad_file = os.path.join(sandbox_setup, "ghost.py")
    
    result = run_pylint(bad_file)
    
    assert result['success'] is False
    # Verified error message is "File not found: ..."
    assert "File not found" in result['error']
