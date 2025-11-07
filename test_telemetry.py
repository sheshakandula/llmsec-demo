#!/usr/bin/env python3
"""
Quick test for telemetry ring buffer
"""
from api.telemetry import log, recent, get_stats, clear_logs

print("📊 Testing Telemetry Ring Buffer\n")
print("=" * 60)

# Clear logs first
clear_logs()
print("✅ Logs cleared\n")

# Test 1: Log some events using flexible log(**kwargs)
print("1. Logging events with log(**kwargs):")
print("-" * 60)

log(endpoint="chat_vuln", event="request", user="alice", message="What is your refund policy?")
log(endpoint="chat_defended", event="request", user="bob", message="Process a refund")
log(endpoint="rag_vuln", event="retrieval", docs=3, sources=["docs/faq.md", "poisoned/refund.md"])
log(endpoint="chat_defended", event="warning", message="Injection detected: instruction_override")
log(endpoint="rag_defended", event="retrieval", docs=2, stripped_lines=5)

print(f"✅ Logged 5 events\n")

# Test 2: Retrieve recent logs
print("2. Retrieving recent logs (n=3):")
print("-" * 60)

logs = recent(n=3)
for i, entry in enumerate(logs, 1):
    endpoint = entry.get("endpoint", "unknown")
    event = entry.get("event", entry.get("event_type", "unknown"))
    message = entry.get("message", "N/A")
    print(f"{i}. [{endpoint}] {event}: {message}")

print(f"\n✅ Retrieved {len(logs)} logs\n")

# Test 3: Get statistics
print("3. Getting telemetry statistics:")
print("-" * 60)

stats = get_stats()
print(f"Total Events: {stats['total_events']}")
print(f"Buffer Used: {stats['buffer_used']}/{stats['buffer_size']}")
print(f"Event Types: {stats['event_types']}")
print(f"Endpoints: {stats['endpoints']}")
print(f"Time Range: {stats['oldest_timestamp']} → {stats['newest_timestamp']}")

print("\n" + "=" * 60)
print("✅ Telemetry test complete!\n")

# Show what the API response would look like
print("📡 API Response Format (/logs/recent?n=50):")
print("-" * 60)
print('{')
print('  "items": [')
print('    {"timestamp": "2024-01-15T10:30:45", "endpoint": "chat_vuln", ...},')
print('    {"timestamp": "2024-01-15T10:31:12", "endpoint": "rag_defended", ...}')
print('  ],')
print('  "count": 5')
print('}')
print()
