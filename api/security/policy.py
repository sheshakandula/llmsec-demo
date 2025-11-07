"""
Tool execution policy for security enforcement
"""
from typing import Dict, Any, List, Optional, Set
import logging
import json

logger = logging.getLogger(__name__)


class ToolPolicy:
    """
    ✅ DEFENDED: Policy enforcement for tool execution

    Features:
    - Allowlist of permitted tools
    - User confirmation requirement for sensitive tools
    - Suspicious argument detection
    - Amount/parameter validation
    """

    def __init__(
        self,
        allowed_tools: Optional[List[str]] = None,
        require_user_confirm: Optional[Set[str]] = None
    ):
        """
        Initialize policy with allowed tools and confirmation requirements

        Args:
            allowed_tools: List of allowed tool names. If None, all tools blocked by default.
            require_user_confirm: Set of tools requiring user confirmation. Defaults to payment_tool.
        """
        self.allowed_tools = set(allowed_tools or [])
        self.require_user_confirm = require_user_confirm or {"payment_tool"}

        logger.info(f"ToolPolicy initialized: allowed={self.allowed_tools}, require_confirm={self.require_user_confirm}")

    def validate_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        ✅ DEFENDED: Validate a tool call against policy

        Checks:
        1. Tool is in allowed list
        2. Arguments don't contain suspicious patterns
        3. Sensitive tools have user confirmation
        4. Tool-specific validation (e.g., amount limits)

        Args:
            tool_name: Name of tool to execute
            args: Tool arguments
            context: Optional context (user_confirmed, session, etc.)

        Returns:
            Tuple of (is_allowed, reason_if_blocked)
        """
        context = context or {}

        # ✅ DEFENDED: Check if tool is in allowed list
        if tool_name not in self.allowed_tools:
            reason = f"Tool '{tool_name}' not in allowed list: {list(self.allowed_tools)}"
            logger.warning(f"Blocked tool call: {reason}")
            return False, reason

        # ✅ DEFENDED: Check for suspicious arguments
        suspicious_check = self._contains_suspicious_args(args)
        if suspicious_check:
            reason = f"Tool arguments contain suspicious pattern: {suspicious_check}"
            logger.warning(f"Blocked tool call: {reason}")
            return False, reason

        # ✅ DEFENDED: Check user confirmation for sensitive tools
        if tool_name in self.require_user_confirm:
            user_confirmed = context.get("user_confirmed", False)

            if not user_confirmed:
                reason = f"Tool '{tool_name}' requires user confirmation"
                logger.warning(f"Blocked tool call: {reason}")
                return False, reason

        # ✅ DEFENDED: Tool-specific validation
        validation_result, validation_reason = self._validate_tool_specific(
            tool_name, args, context
        )

        if not validation_result:
            logger.warning(f"Tool-specific validation failed: {validation_reason}")
            return False, validation_reason

        # All checks passed
        logger.info(f"Tool call validated: {tool_name} with args: {list(args.keys())}")
        return True, None

    def _contains_suspicious_args(self, args: Dict[str, Any]) -> Optional[str]:
        """
        ✅ DEFENDED: Check if arguments contain suspicious patterns

        Args:
            args: Tool arguments dict

        Returns:
            Description of suspicious pattern found, or None if safe
        """
        args_str = json.dumps(args).lower()

        suspicious_patterns = {
            "sql_injection": ["drop table", "delete from", "union select", "'; --"],
            "path_traversal": ["../", "..\\", "/etc/passwd"],
            "code_execution": ["exec(", "eval(", "__import__", "subprocess"],
            "command_injection": ["; rm -rf", "| cat", "&& curl"],
        }

        for category, patterns in suspicious_patterns.items():
            for pattern in patterns:
                if pattern in args_str:
                    return f"{category}: '{pattern}'"

        return None

    def _validate_tool_specific(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
        """
        ✅ DEFENDED: Tool-specific validation logic

        Args:
            tool_name: Tool name
            args: Tool arguments
            context: Optional context

        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        if tool_name == "payment_tool":
            # Validate payment amount
            amount = args.get("amount")

            if amount is None:
                return False, "Missing required 'amount' parameter"

            if not isinstance(amount, (int, float)):
                return False, f"Invalid amount type: {type(amount).__name__}"

            if amount <= 0:
                return False, f"Amount must be positive: {amount}"

            if amount > 10000:
                return False, f"Amount exceeds maximum (10000): {amount}"

            # Validate action
            action = args.get("action")
            if action not in ["charge", "refund"]:
                return False, f"Invalid action: {action}"

            # Validate user_id
            user_id = args.get("user_id")
            if not user_id or not isinstance(user_id, str):
                return False, "Missing or invalid user_id"

        # Add more tool-specific validations here

        return True, None

    def is_allowed(self, tool_name: str) -> bool:
        """
        Quick check if tool is in allowed list

        Args:
            tool_name: Tool name

        Returns:
            True if allowed, False otherwise
        """
        return tool_name in self.allowed_tools

    def requires_confirmation(self, tool_name: str) -> bool:
        """
        Check if tool requires user confirmation

        Args:
            tool_name: Tool name

        Returns:
            True if confirmation required, False otherwise
        """
        return tool_name in self.require_user_confirm
