"""Prompts module for AI agents."""

from .auditor_prompt import AUDITOR_SYSTEM_PROMPT, create_auditor_prompt
from .fixer_prompt import FIXER_SYSTEM_PROMPT, create_fixer_prompt
from .judge_prompt import create_test_generation_prompt

__all__ = [
    'AUDITOR_SYSTEM_PROMPT',
    'create_auditor_prompt',
    'FIXER_SYSTEM_PROMPT',
    'create_fixer_prompt',
    'create_test_generation_prompt'
]
