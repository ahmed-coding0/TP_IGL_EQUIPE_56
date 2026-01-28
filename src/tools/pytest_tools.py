import subprocess
import sys
import os

# Ensure we can import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.files_tools import _validate_path

def run_pytest(file_path: str) -> dict:
    """
    Run pytest on a test file and parse results.
    
    Args:
        file_path: Path to the test file (must be a pytest file inside sandbox)
        
    Returns:
        dict containing:
            - passed: bool - Whether all tests passed
            - total_tests: int
            - passed_tests: int
            - failed_tests: int
            - failures: list - List of failure messages
            - output: str - Complete pytest output
            - success: bool - Whether pytest ran successfully (execution wise)
            - error: str - Execution errors
    """
    result = {
        'passed': False,
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'failures': [],
        'output': '',
        'success': False,
        'error': ''
    }
    
    try:
        # 0. Check existence
        safe_path = _validate_path(file_path)
        if not os.path.exists(safe_path):
            result['error'] = f"File not found: {file_path}"
            return result

        # 1. Run Pytest
        # -v: verbose (helps parsing)
        # --tb=short: short traceback (less clutter)
        # --no-header: removes python version info header
        process = subprocess.run(
            [sys.executable, '-m', 'pytest', safe_path, '-v', '--tb=short', '--no-header'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        result['output'] = process.stdout + '\n' + process.stderr
        result['success'] = True
        
        # 2. Parse Output
        output_lines = result['output'].split('\n')
        
        # Parse summary line: "X passed, Y failed in Zs" or "X passed in Zs"
        for line in output_lines:
            if 'passed' in line or 'failed' in line:
                # Need to be careful not to match random print statements, 
                # usually summary is at the bottom.
                pass_parsed = False
                fail_parsed = False
                
                if 'passed' in line:
                    try:
                        # "5 passed" -> ["5", "passed"]
                        # usually " 5 passed," or "5 passed"
                        parts = line.split('passed')[0].strip().split()
                        if parts and parts[-1].isdigit():
                            result['passed_tests'] = int(parts[-1])
                            pass_parsed = True
                    except (ValueError, IndexError):
                        pass
                
                if 'failed' in line:
                    try:
                        # "... 2 failed ..." 
                        # part before failed
                        parts = line.split('failed')[0].strip().split()
                        if parts and parts[-1].isdigit():
                            result['failed_tests'] = int(parts[-1])
                            fail_parsed = True
                    except (ValueError, IndexError):
                        pass
        
        # Recalculate total logic
        result['total_tests'] = result['passed_tests'] + result['failed_tests']
        
        # Determine global pass status
        # If exit code is 0, usually all passed. 
        # But we rely on parsed counts for granularity. 
        # Pytest exit code 1 means tests failed.
        result['passed'] = (process.returncode == 0) and (result['failed_tests'] == 0) and (result['total_tests'] > 0)

        # 3. Parse Failures (Logic from analysis_tools.py)
        in_failure = False
        failure_buffer = []
        
        for line in output_lines:
            # Start of a failure block usually looks like "FAILED test_file.py::test_name"
            # or "___ test_name ___" depending on output format. 
            # -v gives "test_file.py::test_name FAILED"
            
            # Using logic from analysis_tools.py
            if 'FAILED' in line and '::test_' in line:
                if failure_buffer:
                    result['failures'].append('\n'.join(failure_buffer))
                failure_buffer = [line]
                in_failure = True
            elif in_failure:
                # Look for assertion errors or exception details
                if line.startswith('E ') or 'AssertionError' in line or 'Error:' in line:
                    failure_buffer.append(line)
                elif line.strip() == '' and len(failure_buffer) > 1:
                    # Empty line might signal end of failure block
                    result['failures'].append('\n'.join(failure_buffer))
                    failure_buffer = []
                    in_failure = False
                elif line.startswith('='):
                    # Summary line, end of failures
                    if failure_buffer:
                        result['failures'].append('\n'.join(failure_buffer))
                    break
        
        # Flush remaining buffer
        if failure_buffer:
             result['failures'].append('\n'.join(failure_buffer))
             
    except subprocess.TimeoutExpired:
        result['error'] = "Pytest execution timed out"
        result['output'] += "\nTimeout reached."
    except Exception as e:
        result['error'] = str(e)
        result['output'] += f"\nError: {e}"
        
    return result
