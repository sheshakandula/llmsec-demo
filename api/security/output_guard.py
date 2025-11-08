"""
# UPDATED BY CLAUDE
Output Guard - Parse and validate RUN: directives from LLM output

This module provides utilities to parse "RUN:" directives from LLM responses
and validate them according to security policies.

Pattern: RUN:<action>({"param1": "value1", "param2": "value2"})
Example: RUN:send_email({"to":"user@example.com","subject":"Test","body":"Hello"})
"""
import re
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def parse_run_directive(output: str) -> Optional[Dict[str, Any]]:
    """
    Parse RUN:<action>(<json_payload>) directive from LLM output.

    ⚠️ WARNING: This function extracts potentially malicious directives
    from untrusted LLM output. Always validate results before execution!

    Args:
        output: LLM output text to parse

    Returns:
        Dict with 'action' and 'payload' keys, or None if no directive found

    Examples:
        >>> parse_run_directive("RUN:send_email({\"to\":\"user@example.com\"})")
        {'action': 'send_email', 'payload': {'to': 'user@example.com'}}

        >>> parse_run_directive("Normal text without directives")
        None
    """
    # UPDATED BY CLAUDE: Pattern matches RUN:<action>(<json>)
    # Similar to existing TOOL: pattern but for RUN: directives
    pattern = r'RUN:(\w+)\((\{.*?\})\)'

    match = re.search(pattern, output, re.DOTALL)

    if match:
        action = match.group(1)
        payload_json = match.group(2)

        try:
            payload = json.loads(payload_json)
            logger.info(f"Parsed RUN directive: action={action}, payload keys={list(payload.keys())}")

            return {
                "action": action,
                "payload": payload,
                "raw_match": match.group(0)
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse RUN directive JSON: {e}")
            logger.warning(f"Malformed JSON: {payload_json}")
            return None

    return None


def validate_payload(action: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    ✅ DEFENDED: Validate action payload structure and content

    Security checks:
    - Validates payload is a dict
    - Checks for suspicious patterns in values
    - Validates data types
    - Limits string lengths
    - Detects potential injection attempts

    Args:
        action: Action name
        payload: Action parameters to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # UPDATED BY CLAUDE: Basic type validation
    if not isinstance(payload, dict):
        return False, "Payload must be a dictionary"

    if len(payload) > 20:
        return False, "Too many parameters (max 20)"

    # UPDATED BY CLAUDE: Validate each parameter
    for key, value in payload.items():
        # Key validation
        if not isinstance(key, str):
            return False, f"Parameter key must be string, got {type(key)}"

        if len(key) > 50:
            return False, f"Parameter key '{key}' too long (max 50 chars)"

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            return False, f"Invalid parameter name '{key}' (use alphanumeric and underscore only)"

        # Value validation
        if isinstance(value, str):
            # ✅ DEFENDED: Limit string length
            if len(value) > 5000:
                return False, f"Parameter '{key}' value too long (max 5000 chars)"

            # ✅ DEFENDED: Check for suspicious patterns
            suspicious_patterns = [
                r'<script',  # XSS attempt
                r'javascript:',  # XSS attempt
                r'\$\{.*\}',  # Template injection
                r'\$\(.*\)',  # Command substitution
                r'`.*`',  # Command substitution
                r';\s*(rm|del|drop|delete)\s',  # Destructive commands
                r'(union|select|insert|update|delete).*from',  # SQL injection
            ]

            for pattern in suspicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(f"✅ BLOCKED: Suspicious pattern '{pattern}' in parameter '{key}'")
                    return False, f"Suspicious pattern detected in parameter '{key}'"

        elif isinstance(value, (list, dict)):
            # ✅ DEFENDED: Recursively validate nested structures
            if isinstance(value, dict):
                is_valid, error = validate_payload(action, value)
                if not is_valid:
                    return False, f"Invalid nested payload in '{key}': {error}"
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str) and len(item) > 500:
                        return False, f"List item in '{key}' too long"
                if len(value) > 100:
                    return False, f"List '{key}' too long (max 100 items)"

        elif not isinstance(value, (int, float, bool, type(None))):
            return False, f"Parameter '{key}' has unsupported type {type(value)}"

    return True, None


def sanitize_action_name(action: str) -> str:
    """
    ✅ DEFENDED: Sanitize action name to prevent injection

    Args:
        action: Raw action name from LLM output

    Returns:
        Sanitized action name (alphanumeric and underscore only)
    """
    # UPDATED BY CLAUDE: Remove all non-alphanumeric except underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', action)

    # Limit length
    sanitized = sanitized[:50]

    return sanitized.lower()


def extract_all_run_directives(output: str) -> list[Dict[str, Any]]:
    """
    Extract all RUN: directives from LLM output.

    Useful for detecting multiple action attempts in a single response.

    Args:
        output: LLM output text

    Returns:
        List of parsed directive dicts
    """
    # UPDATED BY CLAUDE: Find all RUN: patterns
    pattern = r'RUN:(\w+)\((\{.*?\})\)'
    matches = re.finditer(pattern, output, re.DOTALL)

    directives = []
    for match in matches:
        action = match.group(1)
        payload_json = match.group(2)

        try:
            payload = json.loads(payload_json)
            directives.append({
                "action": action,
                "payload": payload,
                "raw_match": match.group(0),
                "position": match.start()
            })
        except json.JSONDecodeError:
            logger.warning(f"Skipping malformed RUN directive at position {match.start()}")

    return directives
