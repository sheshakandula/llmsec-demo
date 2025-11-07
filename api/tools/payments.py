"""
Simulated payments tool for demo - NO REAL TRANSACTIONS
"""
from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Audit log location
AUDIT_LOG_PATH = "/tmp/llm_payments_audit.log"


class PaymentRequest(BaseModel):
    """
    Validated payment request model

    Fields:
        to: Recipient identifier (email, user_id, etc.)
        amount: Payment amount (must be positive, max 10000)
    """
    to: str = Field(..., min_length=1, max_length=200, description="Recipient identifier")
    amount: float = Field(..., gt=0, le=10000, description="Payment amount in USD")

    @field_validator('to')
    @classmethod
    def validate_to(cls, v: str) -> str:
        """Validate recipient field"""
        # Remove any suspicious characters
        if any(char in v for char in ['<', '>', '"', "'", ';', '\n', '\r']):
            raise ValueError("Recipient contains invalid characters")
        return v.strip()

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is reasonable"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v > 10000:
            raise ValueError("Amount exceeds maximum (10000)")
        return round(v, 2)  # Round to 2 decimal places


class PaymentsTool:
    """
    🎭 SIMULATED payment processing tool - NO REAL NETWORK CALLS

    All operations are logged to audit file for demo purposes.
    Never performs actual financial transactions.
    """

    @staticmethod
    def dry_run(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate payment action - NO REAL TRANSACTIONS

        Validates input via Pydantic, logs to audit file, returns simulated result.
        NEVER performs actual network calls or real payments.

        Args:
            args: Dictionary with 'to' and 'amount' keys

        Returns:
            Simulated transaction result dict

        Example:
            >>> PaymentsTool.dry_run({"to": "user@example.com", "amount": 50.00})
            {'status': 'simulated', 'to': 'user@example.com', 'amount': 50.0, ...}
        """
        try:
            # ✅ DEFENDED: Validate with Pydantic
            payment = PaymentRequest(**args)

            # Prepare transaction details
            transaction_id = f"sim_{int(datetime.utcnow().timestamp() * 1000)}"
            timestamp = datetime.utcnow().isoformat()

            # Simulate payment processing
            result = {
                "status": "simulated",
                "transaction_id": transaction_id,
                "to": payment.to,
                "amount": payment.amount,
                "timestamp": timestamp,
                "note": "🎭 SIMULATED - No real money transferred"
            }

            # ✅ DEFENDED: Log to audit file (append-only)
            try:
                audit_entry = (
                    f"{timestamp} | TXN:{transaction_id} | "
                    f"TO:{payment.to} | AMOUNT:${payment.amount:.2f} | "
                    f"STATUS:simulated\n"
                )

                # Ensure directory exists
                Path(AUDIT_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

                # Append to audit log
                with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
                    f.write(audit_entry)

                logger.info(f"[DRY RUN] Payment logged: {transaction_id}")

            except Exception as audit_error:
                logger.error(f"Failed to write audit log: {audit_error}")
                # Don't fail the transaction if audit logging fails
                result["audit_warning"] = "Audit logging failed"

            return result

        except ValueError as e:
            # Pydantic validation error
            logger.warning(f"Payment validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "args": args,
                "note": "Validation failed - transaction not processed"
            }

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in payment dry_run: {e}")
            return {
                "status": "error",
                "error": f"Internal error: {str(e)}",
                "note": "Transaction not processed due to error"
            }

    @staticmethod
    def get_audit_log(limit: int = 50) -> str:
        """
        Read recent audit log entries

        Args:
            limit: Maximum number of lines to return

        Returns:
            Audit log contents (last N lines)
        """
        try:
            if not Path(AUDIT_LOG_PATH).exists():
                return "No audit log found"

            with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Return last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            return ''.join(recent_lines)

        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
            return f"Error reading audit log: {e}"

    @staticmethod
    def clear_audit_log() -> bool:
        """
        Clear audit log (for testing purposes only)

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if Path(AUDIT_LOG_PATH).exists():
                Path(AUDIT_LOG_PATH).unlink()
                logger.info("Audit log cleared")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing audit log: {e}")
            return False
