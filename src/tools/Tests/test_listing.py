import os
import sys
import shutil
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.tools.files_tools import list_python_files

@pytest.fixture
def sandbox_setup():
    """Create a temporary directory inside the real sandbox for testing."""
    real_sandbox = os.path.abspath("sandbox")
    os.makedirs(real_sandbox, exist_ok=True)
    
    test_dir = os.path.join(real_sandbox, "test_list_env")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    yield test_dir
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def create_dummy_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write("# test")

def test_list_recursive(sandbox_setup):
    """Test recursive listing of python files."""
    # Create structure:
    # /a.py
    # /subdir/b.py
    # /subdir/subsub/c.py
    
    files = [
        os.path.join(sandbox_setup, "a.py"),
        os.path.join(sandbox_setup, "subdir", "b.py"),
        os.path.join(sandbox_setup, "subdir", "subsub", "c.py"),
        os.path.join(sandbox_setup, "ignore.txt") # Should be ignored
    ]
    
    for f in files:
        create_dummy_file(f)
        
    result = list_python_files(sandbox_setup)
    
    # We expect absolute paths
    expected = sorted([os.path.abspath(f) for f in files if f.endswith(".py")])
    assert result == expected
    assert len(result) == 3

def test_ignore_directories(sandbox_setup):
    """Test that .git and __pycache__ are ignored."""
    
    good_file = os.path.join(sandbox_setup, "good.py")
    
    # These should be ignored
    git_file = os.path.join(sandbox_setup, ".git", "bad.py")
    cache_file = os.path.join(sandbox_setup, "__pycache__", "bad.py")
    venv_file = os.path.join(sandbox_setup, ".venv", "bad.py")
    
    create_dummy_file(good_file)
    create_dummy_file(git_file)
    create_dummy_file(cache_file)
    create_dummy_file(venv_file)
    
    result = list_python_files(sandbox_setup)
    
    assert len(result) == 1
    assert result[0] == os.path.abspath(good_file)

def test_empty_directory(sandbox_setup):
    """Test listing on empty directory."""
    result = list_python_files(sandbox_setup)
    assert result == []

def test_invalid_directory(sandbox_setup):
    """Test that non-existent directory is handled gracefully."""
    bad_dir = os.path.join(sandbox_setup, "does_not_exist")
    # Should print to stderr but not crash, returning empty list
    result = list_python_files(bad_dir)
    assert result == []

def test_security_violation_listing(sandbox_setup):
    """Test that listing outside sandbox returns empty list (and handles error)."""
    # Trying to list the root C drive or project root
    root_dir = os.path.abspath(os.sep) 
    result = list_python_files(root_dir)
    assert result == []

