#!/usr/bin/env python3
"""
Multi-Agent Code Refactoring System using LangGraph.

This system uses three AI agents in a self-healing loop:
1. Auditor: Analyzes code and identifies issues
2. Fixer: Applies corrections to the code
3. Judge: Generates tests and validates fixes
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from src.utils.logger import log_experiment, ActionType
from src.tools import read_file, write_file, list_python_files, run_pylint, run_pytest
from src.prompts import (
    AUDITOR_SYSTEM_PROMPT,
    FIXER_SYSTEM_PROMPT,
    create_auditor_prompt,
    create_fixer_prompt,
    create_test_generation_prompt
)

# Load environment variables
load_dotenv()


def get_llm(agent_type: str = "default", temperature=0.3):
    """
    Get LLM instance based on agent type and LLM_PROVIDER.
    
    Supports:
    - Auditor: Uses Groq Llama 3.3 70B SpecDec (fast analysis)
    - Fixer/Judge: Uses provider from LLM_PROVIDER env var
    
    Args:
        agent_type: "auditor", "fixer", "judge", or "default"
        temperature: Temperature for LLM (default 0.3)
        
    Returns:
        LLM instance (ChatGroq or ChatGoogleGenerativeAI)
    """
    if agent_type == "auditor":
        return ChatGroq(
            model="llama-3.3-70b-versatile",  
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=temperature
        )
    
    # For other agents, use LLM_PROVIDER setting
    provider = os.environ.get("LLM_PROVIDER", "google").lower()
    
    if provider == "groq":
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=temperature
        )
    
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Better for complex tasks
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=temperature,
            convert_system_message_to_human=True
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Use 'google' or 'groq'")


class RefactorState(TypedDict):
    """State schema for the refactoring workflow."""
    file_path: str                    # Path to target Python file
    original_code: Optional[str]      # Original file content
    issues_found: Optional[str]       # Auditor's findings
    fixed_code: Optional[str]         # Fixer's output
    test_results: Optional[str]       # Judge's test execution results
    iteration: int                    # Loop counter (max 10)
    status: Literal["in_progress", "success", "retry", "max_iterations"]


def extract_code_from_markdown(response: str) -> str:
    """
    Extract Python code from markdown code blocks.
    
    Args:
        response: LLM response potentially containing ```python blocks
        
    Returns:
        Extracted code or original response if no blocks found
    """
    if "```python" in response:
        # Extract content between ```python and ```
        parts = response.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0].strip()
            return code
    elif "```" in response:
        # Generic code block
        parts = response.split("```")
        if len(parts) >= 3:
            code = parts[1].strip()
            return code
    
    # No markdown blocks found, return as-is
    return response.strip()


def auditor_node(state: RefactorState) -> RefactorState:
    """
    Auditor Agent: Analyze code and identify issues.
    
    Uses gemini-2.5-flash to perform comprehensive code analysis including
    semantic intent verification, bug detection, and style checking.
    """
    print(f"  🔍 Auditor: Analyzing code...")
    
    file_path = state['file_path']
    code = state['original_code']
    
    # Initialize LLM (provider-independent)
    agent_type = "auditor"
    llm = get_llm(agent_type="auditor", temperature=0.3)  # 🎯 Uses Llama 70B SpecDec
    
    # Run pylint for additional context
    pylint_result = run_pylint(file_path)
    pylint_output = pylint_result.get('raw_output', '')
    
    # Create analysis prompt
    user_prompt = create_auditor_prompt(file_path, code, pylint_output)
    
    try:
        # Call LLM with system prompt
        messages = [
            {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        response = llm.invoke(messages)
        issues_report = response.content
        
        # Rate limit delay
        time.sleep(2)
        
        # Log the interaction
        log_experiment(
            agent_name="Auditor",
            model_used=os.environ.get("LLM_PROVIDER", "google") + "-auditor",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": user_prompt,
                "output_response": issues_report,
                "file_path": file_path,
                "pylint_score": pylint_result.get('score', 0)
            },
            status="SUCCESS"
        )
        
        # Update state
        state['issues_found'] = issues_report
        
        # Count issues for logging
        issue_count = issues_report.count('[CRITICAL]') + issues_report.count('[HIGH]') + issues_report.count('[MEDIUM]')
        print(f"  📊 Auditor: Found {issue_count} issues")
        
    except Exception as e:
        print(f"  ❌ Auditor failed: {e}", file=sys.stderr)
        log_experiment(
            agent_name="Auditor",
            model_used=os.environ.get("LLM_PROVIDER", "google") + "-auditor",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": user_prompt,
                "output_response": f"ERROR: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
        state['issues_found'] = f"ERROR: Analysis failed - {str(e)}"
    
    return state


def fixer_node(state: RefactorState) -> RefactorState:
    """
    Fixer Agent: Apply corrections to code.
    
    Uses gemini-2.5-flash-exp to fix all identified issues while preserving
    functionality and ensuring semantic correctness.
    """
    print(f"  🔧 Fixer: Applying fixes (iteration {state['iteration']})...")
    
    file_path = state['file_path']
    original_code = state['original_code']
    issues = state['issues_found']
    test_failures = state.get('test_results', '')
    
    # Initialize LLM (provider-independent)
    llm = get_llm(agent_type="fixer", temperature=0.3)  # Uses LLM_PROVIDER
    
    # Create fix prompt
    user_prompt = create_fixer_prompt(file_path, original_code, issues, test_failures)
    
    try:
        # Call LLM with system prompt
        messages = [
            {"role": "system", "content": FIXER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        response = llm.invoke(messages)
        fixed_code_raw = response.content
        
        # Rate limit delay
        time.sleep(2)
        
        # Extract code from markdown blocks
        fixed_code = extract_code_from_markdown(fixed_code_raw)
        
        # Log the interaction
        log_experiment(
            agent_name="Fixer",
            model_used=os.environ.get("LLM_PROVIDER", "google") + "-fixer",
            action=ActionType.FIX,
            details={
                "input_prompt": user_prompt,
                "output_response": fixed_code_raw,
                "file_path": file_path,
                "iteration": state['iteration'],
                "had_test_failures": bool(test_failures)
            },
            status="SUCCESS"
        )
        
        # Write fixed code to file
        write_result = write_file(file_path, fixed_code)
        
        if "Success" in write_result:
            state['fixed_code'] = fixed_code
            # Don't increment iteration here - only increment on retry
            print(f"  ✅ Fixer: Code updated successfully")
        else:
            print(f"  ⚠️  Fixer: Failed to write file - {write_result}", file=sys.stderr)
        
    except Exception as e:
        print(f"  ❌ Fixer failed: {e}", file=sys.stderr)
        log_experiment(
            agent_name="Fixer",
            model_used=os.environ.get("LLM_PROVIDER", "google") + "-fixer",
            action=ActionType.FIX,
            details={
                "input_prompt": user_prompt,
                "output_response": f"ERROR: {str(e)}",
                "error": str(e)
            },
            status="FAILURE"
        )
    
    return state


def judge_node(state: RefactorState) -> RefactorState:
    """
    Judge Agent: Generate tests (if needed) and validate fixes.
    
    This agent has two phases:
    1. Generate tests if they don't exist (ActionType.GENERATION)
    2. Run tests and evaluate results (ActionType.DEBUG)
    """
    from pathlib import Path
    from src.prompts.judge_prompt import create_test_generation_prompt
    
    file_path = state['file_path']
    fixed_code = state.get('fixed_code', state.get('original_code', ''))
    issues = state.get('issues_found', '')
    iteration = state.get('iteration', 1)
    
    # Determine test file path
    path_obj = Path(file_path)
    test_file_path = path_obj.parent / f"test_{path_obj.stem}.py"
    
    print(f"  🧪 Judge: Validating fixes...")
    
    # PHASE 1: Generate tests if they don't exist
    if not test_file_path.exists():
        print(f"  📝 Judge: Generating tests...")
        
        try:
            # Initialize LLM (provider-independent)
            llm = get_llm(agent_type="judge", temperature=0.3)  # Uses LLM_PROVIDER
            
            test_prompt = create_test_generation_prompt(file_path, fixed_code, issues)
            
            response = llm.invoke(test_prompt)
            test_code = extract_code_from_markdown(response.content)
            
            # Log test generation
            log_experiment(
                agent_name="Judge",
                model_used=os.environ.get("LLM_PROVIDER", "google") + "-judge-gen",
                action=ActionType.GENERATION,
                details={
                    "file_path": str(test_file_path),
                    "input_prompt": test_prompt,
                    "output_response": response.content,
                    "iteration": iteration
                },
                status="SUCCESS"
            )
            
            # Write test file
            write_file(str(test_file_path), test_code)
            print(f"  ✅ Judge: Tests generated at {test_file_path.name}")
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"  ❌ Judge: Test generation failed: {e}")
            log_experiment(
                agent_name="Judge",
                model_used=os.environ.get("LLM_PROVIDER", "google") + "-judge-gen",
                action=ActionType.GENERATION,
                details={
                    "file_path": str(test_file_path),
                    "input_prompt": test_prompt if 'test_prompt' in locals() else "N/A",
                    "output_response": f"Error: {str(e)}",
                    "iteration": iteration
                },
                status="FAILURE"
            )
            # Continue to test execution anyway (might have old tests)
    
    # PHASE 2: Run tests
    print(f"  🧪 Judge: Running tests...")
    
    try:
        test_results = run_pytest(str(test_file_path))
        
        passed = test_results.get('passed', False)
        total = test_results.get('total_tests', 0)
        passed_count = test_results.get('passed_tests', 0)
        failed_count = test_results.get('failed_tests', 0)
        failures = test_results.get('failures', [])
        raw_output = test_results.get('raw_output', '')
        
        # Log test execution
        log_experiment(
            agent_name="Judge",
            model_used="Judge-pytest",
            action=ActionType.DEBUG,
            details={
                "test_file": str(test_file_path),
                "input_prompt": f"Running pytest on {test_file_path}",
                "output_response": raw_output,
                "passed": passed,
                "total_tests": total,
                "passed_tests": passed_count,
                "failed_tests": failed_count,
                "iteration": iteration
            },
            status="SUCCESS" if passed else "FAILURE"
        )
        
        # Update state based on results
        if total == 0:
            # Try to detect import error
            import_error_detected = "import" in raw_output.lower() or "importerror" in raw_output.lower() or "modulenotfounderror" in raw_output.lower()
            
            if import_error_detected:
                print(f"  ⚠️  Judge: Import error detected - Fixer may have broken function names")
                state['test_results'] = f"IMPORT ERROR - Check test file imports match source file function names:\n{raw_output[:500]}"
            else:
                print(f"  ⚠️  Judge: No tests found or import error")
                state['test_results'] = "No tests collected - possible import error"
            
            state['status'] = "retry" if iteration < 10 else "max_iterations"
        elif passed:
            print(f"  ✅ Judge: All {total} tests passed!")
            state['test_results'] = f"All {total} tests passed"
            state['status'] = "success"
        else:
            print(f"  ❌ Judge: {failed_count}/{total} tests failed")
            failure_msg = "\n".join(failures[:5])  # Limit to first 5 failures
            state['test_results'] = f"Failed {failed_count}/{total} tests:\n{failure_msg}"
            state['status'] = "retry" if iteration < 10 else "max_iterations"
        
        time.sleep(2)  # Rate limiting
        
    except Exception as e:
        print(f"  ❌ Judge: Test execution failed: {e}")
        state['test_results'] = f"Test execution error: {str(e)}"
        state['status'] = "retry" if iteration < 10 else "max_iterations"
        
        log_experiment(
            agent_name="Judge",
            model_used="Judge-pytest",
            action=ActionType.DEBUG,
            details={
                "test_file": str(test_file_path),
                "input_prompt": f"Running pytest on {test_file_path}",
                "output_response": f"Error: {str(e)}",
                "iteration": iteration
            },
            status="FAILURE"
        )
    
    return state


def should_continue(state: RefactorState) -> Literal["fixer", "end"]:
    """
    Decide whether to continue the refactoring loop or finish.
    
    Args:
        state: Current workflow state
        
    Returns:
        "fixer" to loop back for another fix attempt
        "end" to terminate the workflow
    """
    status = state.get('status', 'in_progress')
    
    if status == "retry":
        # Increment iteration counter only when retrying
        state['iteration'] += 1
        return "fixer"
    else:
        # success or max_iterations
        return "end"


def build_workflow():
    """
    Build and compile the LangGraph workflow.
    
    Returns:
        Compiled workflow graph ready for execution
    """
    workflow = StateGraph(RefactorState)
    
    # Add nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge", judge_node)
    
    # Set entry point
    workflow.set_entry_point("auditor")
    
    # Add edges
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    # Conditional edge from judge
    workflow.add_conditional_edges(
        "judge",
        should_continue,
        {
            "fixer": "fixer",
            "end": END
        }
    )
    
    return workflow.compile()


def process_file(file_path: str, workflow) -> dict:
    """
    Process a single Python file through the refactoring workflow.
    
    Args:
        file_path: Path to the Python file to refactor
        workflow: Compiled LangGraph workflow
        
    Returns:
        Dictionary with processing results
    """
    print(f"\n🔍 Processing: {file_path}")
    
    # Read original code
    original_code = read_file(file_path)
    
    if not original_code:
        print(f"  ⚠️  Skipping: Empty or unreadable file")
        return {
            'file': file_path,
            'status': 'skipped',
            'reason': 'empty_or_unreadable'
        }
    
    # Create initial state
    initial_state: RefactorState = {
        'file_path': file_path,
        'original_code': original_code,
        'issues_found': None,
        'fixed_code': None,
        'test_results': None,
        'iteration': 1,
        'status': 'in_progress'
    }
    
    try:
        # Run workflow
        final_state = workflow.invoke(initial_state)
        
        # Prepare result summary
        result = {
            'file': file_path,
            'status': final_state['status'],
            'iterations': final_state['iteration'],
            'issues_found': final_state['issues_found'] is not None,
            'tests_passed': final_state['status'] == 'success'
        }
        
        # Print summary
        status_emoji = {
            'success': '✅',
            'max_iterations': '⚠️',
            'in_progress': '🔄',
            'retry': '🔄'
        }
        
        emoji = status_emoji.get(final_state['status'], '❓')
        print(f"📄 {file_path} -> status: {final_state['status']} {emoji} (iterations: {final_state['iteration']})")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Error processing file: {e}", file=sys.stderr)
        return {
            'file': file_path,
            'status': 'error',
            'error': str(e)
        }


def main():
    """Main entry point for the refactoring system."""
    parser = argparse.ArgumentParser(
        description="Multi-agent code refactoring system using LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target_dir ./sandbox
  python main.py --target_dir ./temp
        """
    )
    
    parser.add_argument(
        '--target_dir',
        required=True,
        help='Directory containing Python files to refactor'
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables", file=sys.stderr)
        print("Please create a .env file with: GOOGLE_API_KEY=your-key-here")
        sys.exit(1)
    
    # Validate target directory
    target_dir = args.target_dir
    if not os.path.exists(target_dir):
        print(f"❌ ERROR: Directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)
    
    print("🚀 Starting Multi-Agent Code Refactoring System")
    print(f"📁 Target directory: {target_dir}\n")
    
    # Find all Python files
    python_files = list_python_files(target_dir)
    
    # Filter out test files (we'll generate those)
    source_files = [f for f in python_files if not os.path.basename(f).startswith('test_')]
    
    if not source_files:
        print(f"⚠️  No Python files found in {target_dir}")
        sys.exit(0)
    
    print(f"📝 Found {len(source_files)} Python file(s) to process\n")
    
    # Build workflow
    workflow = build_workflow()
    
    # Process each file
    results = []
    for file_path in source_files:
        result = process_file(file_path, workflow)
        results.append(result)
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 REFACTORING SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    max_iter_count = sum(1 for r in results if r['status'] == 'max_iterations')
    error_count = sum(1 for r in results if r['status'] == 'error')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    
    print(f"✅ Successful: {success_count}/{len(results)}")
    print(f"⚠️  Max iterations: {max_iter_count}/{len(results)}")
    print(f"❌ Errors: {error_count}/{len(results)}")
    print(f"⏭️  Skipped: {skipped_count}/{len(results)}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_symbol = {
            'success': '✅',
            'max_iterations': '⚠️',
            'error': '❌',
            'skipped': '⏭️'
        }.get(result['status'], '❓')
        
        file_name = os.path.basename(result['file'])
        status = result['status']
        iterations = result.get('iterations', 0)
        
        print(f"  {status_symbol} {file_name:<30} {status:<15} (iterations: {iterations})")
    
    print("\n" + "="*60)
    print(f"📄 Logs saved to: logs/experiment_data.json")
    print("✅ COMPLETE")


if __name__ == "__main__":
    main()