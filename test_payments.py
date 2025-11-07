#!/usr/bin/env python3
"""
Quick test for PaymentsTool dry_run
"""
from api.tools.payments import PaymentsTool

print("💳 Testing PaymentsTool.dry_run()\n")
print("=" * 60)

# Test cases
test_cases = [
    {"to": "alice@example.com", "amount": 50.00},
    {"to": "bob@example.com", "amount": 150.75},
    {"to": "user123", "amount": 25.50},
    {"to": "invalid<script>", "amount": 100.00},  # Invalid chars
    {"to": "charlie@test.com", "amount": -50.00},  # Negative amount
    {"to": "dave@test.com", "amount": 15000.00},  # Exceeds max
    {"to": "", "amount": 50.00},  # Empty recipient
]

for i, args in enumerate(test_cases, 1):
    print(f"\nTest {i}: {args}")
    print("-" * 60)

    result = PaymentsTool.dry_run(args)

    status = result.get("status")
    if status == "simulated":
        print(f"✅ SUCCESS")
        print(f"   Transaction ID: {result['transaction_id']}")
        print(f"   To: {result['to']}")
        print(f"   Amount: ${result['amount']:.2f}")
        print(f"   Note: {result['note']}")
    else:
        print(f"❌ {status.upper()}: {result.get('error', 'Unknown error')}")

# Show audit log
print("\n" + "=" * 60)
print("📋 Audit Log (last 5 entries):")
print("=" * 60)
audit_log = PaymentsTool.get_audit_log(limit=5)
print(audit_log)

print("\n✅ Test complete!\n")
