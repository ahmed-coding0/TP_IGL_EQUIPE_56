import argparse
import sys
import os
#!/usr/bin/env python3
"""Multi-agent code refactoring system using LangGraph."""

import argparse
import os
import sys
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from src.utils.logger import log_experiment, ActionType


# Load environment variables
load_dotenv()

# Define max iterations for refactoring loop
MAX_ITERATIONS = 10


def extract_code_from_markdown(response: str) -> str:
    """Extract Python code from markdown code blocks.
    
    Args:
        response: LLM response that may contain code in markdown blocks
        
    Returns:
        Extracted code without markdown formatting
    """
    if "```python" in response:
        return response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        return response.split("```")[1].split("```")[0].strip()
    return response.strip()

class RefactorState(TypedDict):
    """Shared workflow state passed between agents."""

    file_path: str
    original_code: Optional[str]
    issues_found: Optional[str]
    fixed_code: Optional[str]
    test_results: Optional[str]
    iteration: int
    status: Literal["in_progress", "success", "retry", "max_iterations"]

def auditor_node(state: RefactorState) -> RefactorState:
    """Auditor: Analyze code and identify issues."""
    
    file_path = state["file_path"]
    code = state.get("original_code", "")
    
    print(f"  📊 Auditor analyzing {file_path}...")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    prompt = f"""You are an expert Python code auditor.

Analyze this Python file and identify ALL issues:
- Bugs (logic errors, runtime errors)
- Style violations (PEP8)
- Missing docstrings
- Missing type hints
- Security issues

FILE: {file_path}

CODE:
```python
{code}
```

List each issue with:
1. Line number
2. Issue type (BUG, STYLE, DOCUMENTATION, etc.)
3. Description
4. Severity (HIGH, MEDIUM, LOW)"""

    try:
        response = llm.invoke(prompt)
        issues = response.content
        
        state["issues_found"] = issues
        state["status"] = "in_progress"
        
        # Log the analysis
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": prompt,
                "output_response": issues,
            },
            status="SUCCESS"
        )
        
        print(f"  ✅ Issues found: {len(issues.split(chr(10)))} lines")
        
    except Exception as e:
        error_msg = f"Auditor failed: {e}"
        state["issues_found"] = error_msg
        state["status"] = "retry"
        print(f"  ❌ {error_msg}")
        
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": prompt,
                "output_response": error_msg,
            },
            status="FAILURE"
        )
    
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Path to Python file to analyze")
    args = parser.parse_args()

    file_path = args.file

    if not os.path.exists(file_path):
        print(f"❌ Fichier {file_path} introuvable.")
        sys.exit(1)

    if not file_path.endswith(".py"):
        print(f"❌ Le fichier doit être un fichier .py")
        sys.exit(1)

    print(f"🚀 ANALYSE DU FICHIER : {file_path}")
    
    # Read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"❌ Impossible de lire le fichier : {e}")
        sys.exit(1)
    
    # Create initial state
    state = RefactorState(
        file_path=file_path,
        original_code=code,
        issues_found=None,
        fixed_code=None,
        test_results=None,
        iteration=0,
        status="in_progress"
    )
    
    # Run auditor
    state = auditor_node(state)
    
    print(f"\n📄 {file_path} → status: {state['status']}")
   # print(f"\n🔍 Issues Found:\n{state['issues_found']}")
    print("\n✅ ANALYSE COMPLETE")

if __name__ == "__main__":
    main()