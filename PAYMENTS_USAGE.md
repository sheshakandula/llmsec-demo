# PaymentsTool Usage Examples

## Overview

`PaymentsTool` is a **simulated payment processing tool** that:
- ✅ Validates inputs via Pydantic
- ✅ Logs all transactions to `/tmp/llm_payments_audit.log`
- ✅ **NEVER performs real network calls or actual payments**
- ✅ Returns simulated transaction results

## Installation

First, ensure dependencies are installed:

```bash
pip install -r api/requirements.txt
```

## Basic Usage

### Example 1: Valid Payment

```python
from api.tools.payments import PaymentsTool

# Valid payment request
result = PaymentsTool.dry_run({
    "to": "alice@example.com",
    "amount": 50.00
})

print(result)
# Output:
# {
#     'status': 'simulated',
#     'transaction_id': 'sim_1234567890123',
#     'to': 'alice@example.com',
#     'amount': 50.0,
#     'timestamp': '2024-01-15T10:30:45.123456',
#     'note': '🎭 SIMULATED - No real money transferred'
# }
```

### Example 2: Invalid Amount (Too High)

```python
result = PaymentsTool.dry_run({
    "to": "bob@example.com",
    "amount": 15000.00  # Exceeds max of 10000
})

print(result)
# Output:
# {
#     'status': 'failed',
#     'error': 'Amount exceeds maximum (10000)',
#     'args': {'to': 'bob@example.com', 'amount': 15000.0},
#     'note': 'Validation failed - transaction not processed'
# }
```

### Example 3: Invalid Recipient

```python
result = PaymentsTool.dry_run({
    "to": "user<script>alert('xss')</script>",
    "amount": 100.00
})

print(result)
# Output:
# {
#     'status': 'failed',
#     'error': 'Recipient contains invalid characters',
#     'args': {...},
#     'note': 'Validation failed - transaction not processed'
# }
```

### Example 4: Negative Amount

```python
result = PaymentsTool.dry_run({
    "to": "charlie@test.com",
    "amount": -50.00
})

print(result)
# Output:
# {
#     'status': 'failed',
#     'error': 'Amount must be positive',
#     ...
# }
```

## Audit Log

All successful transactions are logged to `/tmp/llm_payments_audit.log`:

```python
# Get recent audit entries
audit_log = PaymentsTool.get_audit_log(limit=10)
print(audit_log)

# Output:
# 2024-01-15T10:30:45.123456 | TXN:sim_1234567890123 | TO:alice@example.com | AMOUNT:$50.00 | STATUS:simulated
# 2024-01-15T10:31:12.456789 | TXN:sim_1234567890456 | TO:bob@example.com | AMOUNT:$75.50 | STATUS:simulated
```

## Clear Audit Log (Testing Only)

```python
# Clear the audit log
cleared = PaymentsTool.clear_audit_log()
print(f"Audit log cleared: {cleared}")
```

## Validation Rules

The `PaymentRequest` Pydantic model enforces:

1. **`to` field**:
   - Required, non-empty string
   - Max length: 200 characters
   - No special characters: `<`, `>`, `"`, `'`, `;`, `\n`, `\r`

2. **`amount` field**:
   - Required, positive float
   - Minimum: > 0
   - Maximum: ≤ 10000
   - Automatically rounded to 2 decimal places

## Integration with Chat/RAG Endpoints

When used in the chat endpoints, tool calls are validated by the `ToolPolicy`:

```python
from api.security.policy import ToolPolicy

policy = ToolPolicy(allowed_tools=["payment_tool"])

# Validate before execution
is_allowed, reason = policy.validate_tool_call(
    tool_name="payment_tool",
    args={"to": "user@example.com", "amount": 100},
    context={"user_confirmed": True}
)

if is_allowed:
    result = PaymentsTool.dry_run(args)
else:
    print(f"Blocked: {reason}")
```

## Safety Features

✅ **No real network calls** - All transactions are simulated
✅ **Pydantic validation** - Type-safe input validation
✅ **Audit logging** - All transactions logged to file
✅ **Amount limits** - Max $10,000 per transaction
✅ **Character sanitization** - Prevents injection attacks

## Quick Test

Run from project root:

```bash
# Test with the API running
curl -X POST http://localhost:8000/chat/defended \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Process a refund of $50 for user123",
    "user_confirmed": true
  }'
```

The payment tool will be invoked (if the LLM requests it) and the result logged.
