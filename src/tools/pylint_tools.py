import subprocess
import re
import sys
import os
import json

# Ensure we can import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.files_tools import _validate_path

def run_pylint(file_path: str) -> dict:
    """
    Run Pylint static analysis on a Python file.
    
    Args:
        file_path: Path to the Python file to analyze.
        
    Returns:
        dict: containing:
            - score: float (0-10) - Pylint quality score
            - violations: list of dicts - Structured list of errors/warnings
            - output: str - Full output (stdout + stderr)
            - success: bool - Whether the tool ran without crashing
            - error: str - Critical execution errors (e.g. timeout/not found)
    """
    result = {
        'score': 0.0,
        'violations': [],
        'output': '',
        'success': False,
        'error': ''
    }
    
    try:
        # 0. Check existence
        # The _validate_path only checks security (location), not existence.
        # We need to explicitly check if file exists to handle "missing file" case gracefully.
        safe_path = _validate_path(file_path)
        if not os.path.exists(safe_path):
            result['error'] = f"File not found: {file_path}"
            return result

        # 1. Security Check (Done above)
        
        # 2. Run Pylint
        # Use sys.executable -m pylint to ensure we use the installed module in current env
        # This avoids FileNotFoundError on Windows if pylint.exe is not in PATH
        process = subprocess.run(
            [sys.executable, '-m', 'pylint', safe_path, '--output-format=json', '--score=yes'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        result['output'] = process.stdout + process.stderr
        result['success'] = True
        
        # 3. Parse JSON violations
        try:
            if process.stdout.strip():
                # Pylint input might contain non-JSON header text in some versions, 
                # but standard json output usually pure. Safe to try load.
                violations = json.loads(process.stdout)
                result['violations'] = violations
        except json.JSONDecodeError:
            result['violations'] = [] # Fallback
            
        # 4. Extract Score from stderr 
        # (Pylint prints "Your code has been rated at..." in stderr even with json output)
        score_line = [line for line in result['output'].split('\n') 
                     if 'Your code has been rated at' in line]
        if score_line:
            try:
                score_text = score_line[0].split('rated at')[1].split('/')[0].strip()
                result['score'] = float(score_text)
            except (IndexError, ValueError):
                pass
                
    except subprocess.TimeoutExpired:
        result['error'] = "Pylint execution timed out"
        result['output'] += "\nTimeout reached."
    except Exception as e:
        result['error'] = str(e)
        result['output'] += f"\nError: {e}"
        
    return result
