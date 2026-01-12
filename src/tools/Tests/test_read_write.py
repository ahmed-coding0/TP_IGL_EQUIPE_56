import os
import sys
import shutil
import pytest

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.tools.files_tools import read_file, write_file, _validate_path

@pytest.fixture
def sandbox_setup():
    """Create a temporary directory inside the real sandbox for testing."""
    # Ensure main sandbox exists
    real_sandbox = os.path.abspath("sandbox")
    os.makedirs(real_sandbox, exist_ok=True)
    
    # Create test specific sub-sandbox
    test_dir = os.path.join(real_sandbox, "test_rw_env")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    yield test_dir
    
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_write_read_success(sandbox_setup):
    """Test simple write and read sequence."""
    file_path = os.path.join(sandbox_setup, "hello.txt")
    content = "Hello World"
    
    # Write
    result = write_file(file_path, content)
    assert result == "Success"
    
    # Read
    read_content = read_file(file_path)
    assert read_content == content

def test_write_creates_directories(sandbox_setup):
    """Test that nested directories are created automatically."""
    nested_path = os.path.join(sandbox_setup, "deep", "nested", "folder", "test.txt")
    
    result = write_file(nested_path, "data")
    assert result == "Success"
    assert os.path.exists(nested_path)

def test_security_outside_sandbox(sandbox_setup):
    """Test that validating a path outside sandbox raises ValueError."""
    # Try to access a file in the project root (outside sandbox)
    root_file = os.path.abspath("requirements.txt")
    
    with pytest.raises(ValueError) as excinfo:
        _validate_path(root_file)
    assert "outside sandbox" in str(excinfo.value) or "different drive" in str(excinfo.value)

def test_read_non_existent(sandbox_setup):
    """Test reading a file that doesn't exist."""
    missing = os.path.join(sandbox_setup, "ghost.txt")
    content = read_file(missing)
    assert content == ""  # Should return empty string as per spec
