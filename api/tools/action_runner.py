"""
# UPDATED BY CLAUDE
Action Runner Tool - Demonstrates Improper Output Handling vulnerability

This module provides vulnerable and defended implementations of an action
execution system that processes "RUN:" directives from LLM output.

⚠️ VULNERABLE: Blindly executes actions parsed from LLM output
✅ DEFENDED: Validates payloads and requires user confirmation
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionRunner:
    """
    Simulated action runner demonstrating improper output handling vulnerability.

    This is a DEMO ONLY tool - no real network calls or shell execution.
    All actions are simulated and logged for educational purposes.
    """

    # UPDATED BY CLAUDE: Demo-safe allowed actions
    ALLOWED_ACTIONS = {
        "send_email": ["to", "subject", "body"],
        "create_ticket": ["title", "description", "priority"],
        "schedule_meeting": ["attendees", "time", "duration"],
        "update_status": ["resource_id", "status"],
        "send_notification": ["user_id", "message"]
    }

    # UPDATED BY CLAUDE: Dangerous actions that should require confirmation
    DANGEROUS_ACTIONS = {"send_email", "create_ticket", "schedule_meeting"}

    @staticmethod
    def execute_vuln(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⚠️ VULNERABLE: Execute action without validation

        Security issues:
        - No payload validation
        - No action allowlist check
        - No user confirmation required
        - Blindly trusts LLM output

        Args:
            action: Action name from LLM output
            payload: Action parameters from LLM output

        Returns:
            Simulated execution result
        """
        log_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "payload": payload,
            "mode": "vulnerable"
        }

        logger.warning(f"⚠️ VULNERABLE ACTION EXECUTION: {action} with payload {payload}")

        # ⚠️ VULNERABLE: No validation - just execute
        if action == "send_email":
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Email sent to {payload.get('to', 'unknown')}",
                "warning": "⚠️ No validation performed - vulnerable to injection",
                "log": log_event
            }
        elif action == "create_ticket":
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Ticket created: {payload.get('title', 'Untitled')}",
                "ticket_id": "TICK-12345",
                "warning": "⚠️ No validation performed - vulnerable to injection",
                "log": log_event
            }
        elif action == "schedule_meeting":
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Meeting scheduled with {payload.get('attendees', [])}",
                "meeting_id": "MEET-67890",
                "warning": "⚠️ No validation performed - vulnerable to injection",
                "log": log_event
            }
        elif action == "update_status":
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Status updated for {payload.get('resource_id', 'unknown')}",
                "warning": "⚠️ No validation performed - vulnerable to injection",
                "log": log_event
            }
        elif action == "send_notification":
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Notification sent to {payload.get('user_id', 'unknown')}",
                "warning": "⚠️ No validation performed - vulnerable to injection",
                "log": log_event
            }
        else:
            # ⚠️ VULNERABLE: Even unknown actions get attempted
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Unknown action '{action}' executed anyway",
                "warning": "⚠️ CRITICAL: Unknown action executed without validation!",
                "log": log_event
            }

    @staticmethod
    def execute_defended(action: str, payload: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """
        ✅ DEFENDED: Execute action with validation and confirmation

        Security measures:
        - Validates action against allowlist
        - Validates payload structure
        - Requires user confirmation for dangerous actions
        - Sanitizes parameters

        Args:
            action: Action name from LLM output
            payload: Action parameters from LLM output
            user_confirmed: Whether user explicitly confirmed execution

        Returns:
            Validated execution result or blocked response
        """
        log_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "payload": payload,
            "user_confirmed": user_confirmed,
            "mode": "defended"
        }

        # ✅ DEFENDED: Validate action is in allowlist
        if action not in ActionRunner.ALLOWED_ACTIONS:
            logger.warning(f"✅ BLOCKED: Unknown action '{action}' not in allowlist")
            return {
                "status": "blocked",
                "action": action,
                "reason": "action_not_allowed",
                "message": f"Action '{action}' is not in the allowlist",
                "allowed_actions": list(ActionRunner.ALLOWED_ACTIONS.keys()),
                "log": log_event
            }

        # ✅ DEFENDED: Validate payload has required fields
        required_fields = ActionRunner.ALLOWED_ACTIONS[action]
        missing_fields = [f for f in required_fields if f not in payload]
        if missing_fields:
            logger.warning(f"✅ BLOCKED: Missing required fields for {action}: {missing_fields}")
            return {
                "status": "blocked",
                "action": action,
                "reason": "invalid_payload",
                "message": f"Missing required fields: {missing_fields}",
                "required_fields": required_fields,
                "log": log_event
            }

        # ✅ DEFENDED: Require user confirmation for dangerous actions
        if action in ActionRunner.DANGEROUS_ACTIONS and not user_confirmed:
            logger.info(f"✅ PENDING: Dangerous action '{action}' requires user confirmation")
            return {
                "status": "pending_confirmation",
                "action": action,
                "reason": "user_confirmation_required",
                "message": f"Action '{action}' requires explicit user confirmation",
                "payload": payload,
                "log": log_event
            }

        # ✅ DEFENDED: Sanitize and execute with validation
        logger.info(f"✅ DEFENDED ACTION EXECUTION: {action} (validated and confirmed)")

        if action == "send_email":
            # ✅ DEFENDED: Sanitize email parameters
            to_addr = str(payload.get('to', ''))[:100]  # Limit length
            subject = str(payload.get('subject', ''))[:200]
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Validated email sent to {to_addr}",
                "sanitized": True,
                "log": log_event
            }
        elif action == "create_ticket":
            title = str(payload.get('title', ''))[:100]
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Validated ticket created: {title}",
                "ticket_id": "TICK-SAFE-12345",
                "sanitized": True,
                "log": log_event
            }
        elif action == "schedule_meeting":
            attendees = payload.get('attendees', [])
            if not isinstance(attendees, list):
                attendees = [str(attendees)]
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Validated meeting scheduled with {len(attendees)} attendee(s)",
                "meeting_id": "MEET-SAFE-67890",
                "sanitized": True,
                "log": log_event
            }
        elif action == "update_status":
            resource_id = str(payload.get('resource_id', ''))[:50]
            status = str(payload.get('status', ''))[:50]
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Status updated for {resource_id} to {status}",
                "sanitized": True,
                "log": log_event
            }
        elif action == "send_notification":
            user_id = str(payload.get('user_id', ''))[:50]
            message = str(payload.get('message', ''))[:500]
            return {
                "status": "executed",
                "action": action,
                "result": f"[SIMULATED] Notification sent to {user_id}",
                "sanitized": True,
                "log": log_event
            }

        # Should never reach here due to allowlist check above
        return {
            "status": "error",
            "action": action,
            "reason": "internal_error",
            "message": "Unexpected execution path",
            "log": log_event
        }
