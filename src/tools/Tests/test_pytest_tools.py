import os
import sys
import shutil
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.tools.pytest_tools import run_pytest
from src.tools.files_tools import write_file

@pytest.fixture
def sandbox_setup():
    """Create a temporary directory inside the real sandbox for testing."""
    real_sandbox = os.path.abspath("sandbox")
    os.makedirs(real_sandbox, exist_ok=True)
    
    test_dir = os.path.join(real_sandbox, "test_pytest_env")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    yield test_dir
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_pytest_success(sandbox_setup):
    """Test pytest on a file with passing tests."""
    test_code = '''
def test_one():
    assert 1 == 1

def test_two():
    assert "a" in "abc"
'''
    file_path = os.path.join(sandbox_setup, "test_pass.py")
    write_file(file_path, test_code)
    
    result = run_pytest(file_path)
    
    assert result['success'] is True
    assert result['passed'] is True
    assert result['passed_tests'] == 2
    assert result['failed_tests'] == 0

def test_pytest_failure(sandbox_setup):
    """Test pytest on a file with failing tests."""
    test_code = '''
def test_pass():
    assert True

def test_fail():
    assert 1 == 2
'''
    file_path = os.path.join(sandbox_setup, "test_fail.py")
    write_file(file_path, test_code)
    
    result = run_pytest(file_path)
    
    assert result['success'] is True
    assert result['passed'] is False
    assert result['passed_tests'] == 1
    assert result['failed_tests'] == 1
    assert len(result['failures']) > 0
    assert "test_fail" in result['failures'][0] or "assert 1 == 2" in result['failures'][0]

def test_pytest_syntax_error(sandbox_setup):
    """Test pytest on a file with syntax error."""
    test_code = '''
def test_broken()
    assert True
'''
    file_path = os.path.join(sandbox_setup, "test_broken.py")
    write_file(file_path, test_code)
    
    result = run_pytest(file_path)
    
    # Execution succeeds (tool runs), but collection fails or test fails with error
    assert result['success'] is True
    assert result['passed'] is False
    # Standard pytest output for syntax error usually sends 'collected 0 items' and exit code 4 (Usage Error) or 2 (Interrupted)
    # Output should contain information about the error
    assert "SyntaxError" in result['output'] or "syntax-error" in result['output']

def test_security_violation_pytest(sandbox_setup):
    """Test run_pytest outside sandbox."""
    outside_file = os.path.abspath("main.py")
    
    result = run_pytest(outside_file)
    
    assert result['success'] is False
    assert "outside sandbox" in result['error'] or "different drive" in result['error']

def test_missing_file_pytest(sandbox_setup):
    """Test run_pytest on non-existent file."""
    bad_file = os.path.join(sandbox_setup, "ghost_test.py")
    
    result = run_pytest(bad_file)
    
    assert result['success'] is False
    assert "File not found" in result['error']
