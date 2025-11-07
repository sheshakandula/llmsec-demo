"""
In-memory telemetry logger for demo purposes

Simple ring buffer implementation for logging API events
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

# In-memory log storage (ring buffer with max size)
LOG_STORE: deque = deque(maxlen=200)


def log(**kwargs) -> None:
    """
    Log an event to in-memory ring buffer

    Accepts any keyword arguments and stores them as a log entry.
    Automatically adds timestamp if not provided.

    Args:
        **kwargs: Arbitrary keyword arguments to log

    Example:
        >>> log(endpoint="chat", event="request", user="test")
        >>> log(endpoint="rag", event="retrieval", docs=3, message="Retrieved docs")
    """
    # Add timestamp if not provided
    if "timestamp" not in kwargs:
        kwargs["timestamp"] = datetime.utcnow().isoformat()

    # Truncate message if present
    if "message" in kwargs and isinstance(kwargs["message"], str):
        kwargs["message"] = kwargs["message"][:500]

    # Store entry
    LOG_STORE.append(kwargs)

    # Also log to standard logger
    endpoint = kwargs.get("endpoint", "unknown")
    event_type = kwargs.get("event_type", kwargs.get("event", "info"))
    message = kwargs.get("message", str(kwargs))

    log_level = logging.WARNING if event_type == "warning" else logging.INFO
    logger.log(log_level, f"[{endpoint}] {message[:200]}")


def log_event(
    endpoint: str,
    event_type: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an event to in-memory store (legacy interface)

    Args:
        endpoint: API endpoint name
        event_type: Type of event (request, warning, error, etc.)
        message: Log message
        metadata: Additional metadata
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "event_type": event_type,
        "message": message[:500],  # Truncate long messages
        "metadata": metadata or {}
    }

    LOG_STORE.append(entry)

    # Also log to standard logger
    log_level = logging.WARNING if event_type == "warning" else logging.INFO
    logger.log(log_level, f"[{endpoint}] {message[:200]}")


def recent(n: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve recent logs from ring buffer

    Args:
        n: Number of recent logs to return (default: 50)

    Returns:
        List of log entry dicts (most recent last)
    """
    # Clamp n to reasonable bounds
    n = max(1, min(n, len(LOG_STORE)))

    # Return last n entries
    return list(LOG_STORE)[-n:]


def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve recent logs from in-memory store (legacy interface)

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of log entries
    """
    return recent(n=limit)


def clear_logs() -> None:
    """Clear all logs (for testing)"""
    LOG_STORE.clear()
    logger.info("All logs cleared")


def get_stats() -> Dict[str, Any]:
    """
    Get telemetry statistics

    Returns:
        Dictionary with stats about logged events
    """
    if not LOG_STORE:
        return {
            "total_events": 0,
            "buffer_size": 200,
            "buffer_used": 0
        }

    # Count events by type
    event_types = {}
    endpoints = {}

    for entry in LOG_STORE:
        event_type = entry.get("event_type", entry.get("event", "unknown"))
        endpoint = entry.get("endpoint", "unknown")

        event_types[event_type] = event_types.get(event_type, 0) + 1
        endpoints[endpoint] = endpoints.get(endpoint, 0) + 1

    return {
        "total_events": len(LOG_STORE),
        "buffer_size": LOG_STORE.maxlen,
        "buffer_used": len(LOG_STORE),
        "event_types": event_types,
        "endpoints": endpoints,
        "oldest_timestamp": LOG_STORE[0].get("timestamp") if LOG_STORE else None,
        "newest_timestamp": LOG_STORE[-1].get("timestamp") if LOG_STORE else None
    }
