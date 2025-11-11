"""
Standardized Response Helper for LLMSec Demo
Ensures consistent field ordering across all API endpoints
"""
from typing import Any, Dict, Optional


def build_response(
    *,
    tool_result: Optional[dict] = None,
    answer: str | None = None,
    response: str | None = None,
    **meta: Any
) -> Dict[str, Any]:
    """
    Standardized output wrapper for all endpoints.

    Always returns fields in this order:
      1. answer       - Primary answer text (RAG endpoints) - SHOWS FIRST in UI
      2. response     - Primary response text (Chat endpoints) - SHOWS FIRST in UI
      3. tool_result  - Result from tool execution (if any) - Secondary details
      4. metadata     - Additional fields in alphabetical order

    This ordering ensures the most important content (answer/response) appears
    at the top of the JSON when displayed in the UI.

    Args:
        tool_result: Optional tool execution result dict
        answer: Optional answer text (used by RAG endpoints)
        response: Optional response text (used by Chat endpoints)
        **meta: Additional metadata fields (blocked, hits, sources, warning, etc.)

    Returns:
        OrderedDict with UI-friendly field ordering

    Examples:
        >>> build_response(answer="The refund policy is...", sources=["faq.md"])
        {'answer': 'The refund policy is...', 'response': '', 'tool_result': None, 'sources': ['faq.md']}

        >>> build_response(response="Hello!", tool_result={"success": True}, warning="Vulnerable")
        {'answer': '', 'response': 'Hello!', 'tool_result': {'success': True}, 'warning': 'Vulnerable'}
    """
    # Build ordered response - Python 3.7+ dict insertion order is preserved
    # REVERSED ORDER: answer/response first for UI readability
    out = {
        "answer": answer or "",
        "response": response or "",
        "tool_result": tool_result
    }

    # Add metadata fields in alphabetical order for consistency
    sorted_meta = dict(sorted(meta.items()))
    out.update(sorted_meta)

    return out
