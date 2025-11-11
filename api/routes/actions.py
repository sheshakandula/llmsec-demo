"""
# UPDATED BY CLAUDE
Actions API Routes - Improper Output Handling Demo

This module provides API endpoints for demonstrating the "Improper Output Handling"
vulnerability where applications blindly execute actions parsed from LLM output.

Endpoints:
- POST /actions/run/vuln - Vulnerable: Executes actions without validation
- POST /actions/run/defended - Defended: Validates and requires confirmation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from api.tools.action_runner import ActionRunner
from api.security.output_guard import (
    parse_run_directive,
    validate_payload,
    sanitize_action_name,
    extract_all_run_directives
)
from api.telemetry import log_event
from api.utils.respond import build_response  # STANDARDIZATION

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Models
class ActionRequest(BaseModel):
    """
    Request to execute an action from LLM output.

    In a real application, this would be the LLM's response text
    containing RUN: directives that the application parses and executes.
    """
    llm_output: str = Field(..., description="LLM output containing RUN: directive(s)")
    user_confirmed: bool = Field(default=False, description="User explicitly confirmed execution")


class ActionResponse(BaseModel):
    """Response from action execution - STANDARDIZATION: UI-friendly ordering"""
    answer: str = ""  # STANDARDIZATION: Position 1 - SHOWS FIRST in UI
    response: str = ""  # STANDARDIZATION: Position 2 - SHOWS FIRST in UI
    tool_result: Optional[Dict[str, Any]] = None  # STANDARDIZATION: Position 3 (alias for execution_result)
    # Metadata fields (alphabetical):
    action: Optional[str] = None
    blocked: Optional[bool] = None
    execution_result: Optional[Dict[str, Any]] = None  # Legacy field (use tool_result)
    message: Optional[str] = None
    parsed_directive: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    result: Optional[str] = None
    status: str
    warning: Optional[str] = None


@router.post("/run/vuln", response_model=ActionResponse)
async def run_action_vuln(request: ActionRequest):
    """
    ⚠️ VULNERABLE: Execute action from LLM output without validation

    Security issues demonstrated:
    - Blindly parses and executes RUN: directives from untrusted LLM output
    - No validation of action or payload
    - No user confirmation required
    - Trusts LLM to make safe decisions about actions

    Example attack:
    ```
    POST /actions/run/vuln
    {
        "llm_output": "Sure! RUN:send_email({\"to\":\"admin@company.com\",\"subject\":\"Reset all passwords\",\"body\":\"Urgent\"})"
    }
    ```

    This will execute the email send WITHOUT validation or confirmation.
    """
    log_event("actions_vuln", "request", f"Received LLM output: {request.llm_output[:100]}...")

    # ⚠️ VULNERABLE: Parse RUN directive from untrusted LLM output
    directive = parse_run_directive(request.llm_output)

    if not directive:
        log_event("actions_vuln", "no_directive", "No RUN directive found in output")
        return ActionResponse(**build_response(
            tool_result=None,
            answer="",
            response="",
            action=None,
            execution_result=None,
            message="No RUN: directive found in LLM output",
            status="no_action",
            warning="⚠️ This endpoint is vulnerable to improper output handling"
        ))

    action = directive["action"]
    payload = directive["payload"]

    log_event("actions_vuln", "executing", f"⚠️ Executing {action} WITHOUT validation")

    # ⚠️ VULNERABLE: Execute without any validation or confirmation
    result = ActionRunner.execute_vuln(action, payload)

    return ActionResponse(**build_response(
        tool_result=result,
        answer="",
        response="",
        action=action,
        execution_result=result,
        parsed_directive=directive,
        result=result.get("result"),
        status="executed",
        warning="⚠️ Action executed without validation - vulnerable to LLM manipulation"
    ))


@router.post("/run/defended", response_model=ActionResponse)
async def run_action_defended(request: ActionRequest):
    """
    ✅ DEFENDED: Execute action with validation and confirmation

    Security measures:
    - Parses RUN: directive but validates before execution
    - Validates action is in allowlist
    - Validates payload structure and content
    - Requires user confirmation for dangerous actions
    - Sanitizes all parameters
    - Logs all attempts

    Example safe execution:
    ```
    POST /actions/run/defended
    {
        "llm_output": "RUN:send_email({\"to\":\"user@example.com\",\"subject\":\"Report\",\"body\":\"Here is your report\"})",
        "user_confirmed": true
    }
    ```

    This will validate the action and require confirmation before executing.
    """
    log_event("actions_defended", "request", f"Received LLM output: {request.llm_output[:100]}...")

    # ✅ DEFENDED: Parse directive (same as vulnerable, but validate afterwards)
    directive = parse_run_directive(request.llm_output)

    if not directive:
        log_event("actions_defended", "no_directive", "No RUN directive found in output")
        return ActionResponse(**build_response(
            tool_result=None,
            answer="",
            response="",
            message="No RUN: directive found in LLM output",
            status="no_action"
        ))

    raw_action = directive["action"]
    payload = directive["payload"]

    # ✅ DEFENDED: Sanitize action name
    action = sanitize_action_name(raw_action)

    if action != raw_action:
        log_event("actions_defended", "sanitized", f"Sanitized action '{raw_action}' -> '{action}'")

    # ✅ DEFENDED: Validate payload structure
    is_valid, error_msg = validate_payload(action, payload)
    if not is_valid:
        log_event("actions_defended", "blocked", f"Invalid payload: {error_msg}")
        return ActionResponse(**build_response(
            tool_result=None,
            answer="",
            response="",
            action=action,
            blocked=True,
            execution_result=None,
            message=f"Payload validation failed: {error_msg}",
            parsed_directive=directive,
            reason="invalid_payload",
            status="blocked",
            warning=None
        ))

    log_event("actions_defended", "validated", f"✅ Action {action} passed validation")

    # ✅ DEFENDED: Execute with validation and confirmation checks
    result = ActionRunner.execute_defended(action, payload, request.user_confirmed)

    # Check if execution was blocked or pending
    if result["status"] == "blocked":
        return ActionResponse(**build_response(
            tool_result=result,
            answer="",
            response="",
            action=action,
            blocked=True,
            execution_result=result,
            message=result.get("message"),
            parsed_directive=directive,
            reason=result.get("reason"),
            status="blocked",
            warning=None
        ))
    elif result["status"] == "pending_confirmation":
        return ActionResponse(**build_response(
            tool_result=result,
            answer="",
            response="",
            action=action,
            execution_result=result,
            message=result.get("message"),
            parsed_directive=directive,
            reason=result.get("reason"),
            status="pending_confirmation",
            warning=None
        ))

    # Successfully executed
    log_event("actions_defended", "executed", f"✅ Action {action} executed successfully")

    return ActionResponse(**build_response(
        tool_result=result,
        answer="",
        response="",
        action=action,
        execution_result=result,
        parsed_directive=directive,
        result=result.get("result"),
        status="executed",
        warning=None
    ))


@router.get("/info")
async def get_actions_info():
    """
    Get information about the actions demo.

    Returns:
        Info about available actions and security patterns
    """
    return {
        "demo": "Improper Output Handling",
        "description": "Demonstrates vulnerability when applications blindly execute actions from LLM output",
        "vulnerable_endpoint": "/actions/run/vuln",
        "defended_endpoint": "/actions/run/defended",
        "pattern": "RUN:<action>({\"param\": \"value\"})",
        "example": "RUN:send_email({\"to\":\"user@example.com\",\"subject\":\"Test\",\"body\":\"Hello\"})",
        "allowed_actions": list(ActionRunner.ALLOWED_ACTIONS.keys()),
        "security_measures": [
            "Action allowlist validation",
            "Payload structure validation",
            "User confirmation for dangerous actions",
            "Parameter sanitization",
            "Suspicious pattern detection",
            "Comprehensive logging"
        ]
    }
