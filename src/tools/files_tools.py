import os
import sys

def _validate_path(file_path: str) -> str:
    """
    Internal utility: Normalize path and ensure it's within the 'sandbox' directory.
    
    Args:
        file_path: The path to validate.
        
    Returns:
        The absolute path if valid.
        
    Raises:
        ValueError: If the path is outside the sandbox.
    """
    # Determine the sandbox root directory (relative to where this script runs)
    # Assuming the script runs from the project root where 'sandbox' exists
    sandbox_root = os.path.abspath("sandbox")
    
    # Convert input path to absolute
    abs_path = os.path.abspath(file_path)
    
    # Check if the path starts with the sandbox root
    # commonpath raises ValueError on Windows if drives are different
    try:
        common = os.path.commonpath([sandbox_root, abs_path])
    except ValueError:
        raise ValueError(f"Security Error: Path '{file_path}' is on a different drive than sandbox.")

    if common != sandbox_root:
        raise ValueError(f"Security Error: Access to '{file_path}' is denied (outside sandbox).")
        
    return abs_path

def read_file(file_path: str) -> str:
    """
    Read content from file_path; return empty string on error.
    
    Args:
        file_path: Path to the file to read.
        
    Returns:
        Content of the file as success, or empty string on failure.
        Errors are printed to stderr for logging purposes.
    """
    try:
        safe_path = _validate_path(file_path)
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        return ""

def write_file(file_path: str, content: str) -> str:
    """
    Write content to file_path, creating parent directories if needed.
    
    Args:
        file_path: Path to the file to write.
        content: The string content to write.
        
    Returns:
        "Success" if the operation succeeded, or an error message string if it failed.
    """
    try:
        safe_path = _validate_path(file_path)
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "Success"
    except Exception as e:
        error_msg = f"Error writing file '{file_path}': {e}"
        print(error_msg, file=sys.stderr)
        return error_msg
    

def list_python_files(directory: str = "sandbox") -> list[str]:
    """
    Recursively collect all .py files under directory (excluding __pycache__), sorted.
    
    Args:
        directory: The root directory to search (default: "sandbox").
        
    Returns:
        A sorted list of absolute paths to .py files.
    """
    python_files = []
    try:
        # If directory is not absolute, treat it as relative to CWD (usually project root)
        # But we must ensure it's inside the sandbox for security
        # If user passes ".", check if CWD is safe? 
        # For this specific tool, 'directory' acts as the start point INSIDE sandbox.
        
        # Security: Allow users to pass subdirs of sandbox, but default to sandbox root.
        # If 'directory' is absolute, validate it. If relative, join with sandbox implicitly?
        # The safest approach given requirements: validate provided directory.
        
        safe_dir = _validate_path(directory)
        
        for root, dirs, files in os.walk(safe_dir):
            # inplace filter to skip common ignored dirs
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.abspath(os.path.join(root, file)))
                    
        return sorted(python_files)
        
    except Exception as e:
        print(f"Error listing python files in '{directory}': {e}", file=sys.stderr)
        return []

