"""
Security filters for detecting and sanitizing inputs
"""
import re
import html
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def detect_injection(text: str) -> Optional[str]:
    """
    Detect common prompt injection patterns

    Checks for:
    - Instruction override attempts ("ignore previous instructions")
    - System prompt revelation ("reveal system prompt")
    - Role switching ("you are now")
    - Delimiter injection (###, <|...|>)
    - Tool injection patterns (TOOL:)

    Args:
        text: Input text to check

    Returns:
        Description of detected pattern, or None if safe
    """
    patterns = {
        "instruction_override": r"(ignore|disregard|forget).*(previous|above|prior|earlier).*(instruction|prompt|rule)",
        "system_reveal": r"(reveal|show|display|print|output).*(system|prompt|instruction)",
        "role_switch": r"(you are now|act as|pretend to be|roleplay as|from now on)",
        "delimiter_injection": r"(###|<\|.*?\|>|\[INST\]|\[/INST\]|<\|im_start\|>|<\|im_end\|>)",
        "system_override": r"(system\s*:|new system prompt|override system|update system)",
        "context_manipulation": r"(ignore (the )?context|disregard (the )?context|bypass context)",
        "tool_injection": r"TOOL\s*:\s*\w+\s*\(",
        "command_injection": r"(\\n\\n|\\r\\n|```).*system",
    }

    for pattern_name, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Injection pattern detected: {pattern_name} in text: {text[:100]}")
            return pattern_name

    return None


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """
    ✅ DEFENDED: Sanitize user input

    - Strips HTML tags and entities
    - Removes control characters
    - Neutralizes TOOL: patterns
    - Normalizes whitespace
    - Truncates to max length

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Truncate to max length first
    text = text[:max_length]

    # Remove null bytes and other control characters
    text = text.replace('\x00', '')
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Neutralize TOOL: patterns by adding space
    text = re.sub(r'TOOL\s*:', 'TOOL_ :', text, flags=re.IGNORECASE)

    # Remove excessive newlines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize whitespace (but preserve single newlines)
    lines = text.split('\n')
    normalized_lines = [' '.join(line.split()) for line in lines]
    text = '\n'.join(normalized_lines)

    return text.strip()


def parse_tool_request_from_output(output: str) -> Optional[Dict[str, Any]]:
    """
    Parse tool/function call requests from LLM output

    Supports multiple formats:
    1. XML-style: <tool>tool_name</tool><args>{"key": "value"}</args>
    2. TOOL_REQUEST JSON: TOOL_REQUEST {"name": "...", "args": {...}}
    3. Simple TOOL: format: TOOL:tool_name({"key": "value"})

    Args:
        output: LLM output text

    Returns:
        Parsed tool request dict, or None if no tool call found
    """
    # Try XML-style format first
    tool_pattern = r'<tool>(.*?)</tool>'
    args_pattern = r'<args>(.*?)</args>'

    tool_match = re.search(tool_pattern, output, re.DOTALL)
    args_match = re.search(args_pattern, output, re.DOTALL)

    if tool_match:
        tool_name = tool_match.group(1).strip()
        args_str = args_match.group(1).strip() if args_match else "{}"

        try:
            import json
            args = json.loads(args_str)
            return {
                "tool": tool_name,
                "args": args
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse XML-style tool args: {e}")
            return None

    # Try TOOL_REQUEST format
    tool_request_pattern = r'TOOL_REQUEST\s+(\{[\s\S]*?\})'
    request_match = re.search(tool_request_pattern, output)

    if request_match:
        json_str = request_match.group(1)

        try:
            import json
            tool_request = json.loads(json_str)

            if "name" in tool_request and "args" in tool_request:
                return {
                    "tool": tool_request["name"],
                    "args": tool_request["args"],
                    "rationale": tool_request.get("rationale", "")
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TOOL_REQUEST: {e}")
            return None

    # Try simple TOOL: format
    simple_pattern = r'TOOL:(\w+)\((\{.*?\})\)'
    simple_match = re.search(simple_pattern, output, re.DOTALL)

    if simple_match:
        tool_name = simple_match.group(1)
        args_json = simple_match.group(2)

        try:
            import json
            args = json.loads(args_json)
            return {
                "tool": tool_name,
                "args": args
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse simple TOOL: format: {e}")
            return None

    return None
