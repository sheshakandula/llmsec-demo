"""
Debug and logging endpoints
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Any

from api.telemetry import recent, get_recent_logs, clear_logs, get_stats

router = APIRouter()


class LogsResponse(BaseModel):
    """Logs response model with items list"""
    items: List[Dict[str, Any]]
    count: int


class StatsResponse(BaseModel):
    """Telemetry statistics response"""
    total_events: int
    buffer_size: int
    buffer_used: int
    event_types: Dict[str, int]
    endpoints: Dict[str, int]
    oldest_timestamp: str | None
    newest_timestamp: str | None


@router.get("/recent")
async def get_recent_logs_endpoint(
    n: int = Query(default=50, ge=1, le=200, description="Number of recent logs to retrieve")
) -> Dict[str, Any]:
    """
    Retrieve recent API request logs from in-memory ring buffer

    Args:
        n: Number of recent logs to return (default: 50, max: 200)

    Returns:
        JSON with {"items": [...], "count": N}
    """
    logs = recent(n=n)

    return {
        "items": logs,
        "count": len(logs)
    }


@router.get("/stats", response_model=StatsResponse)
async def get_telemetry_stats() -> StatsResponse:
    """
    Get telemetry statistics

    Returns statistics about logged events, including:
    - Total events logged
    - Buffer usage
    - Event type breakdown
    - Endpoint breakdown
    - Timestamp range
    """
    stats = get_stats()
    return StatsResponse(**stats)


@router.post("/clear")
async def clear_logs_endpoint():
    """
    Clear all logs (for testing/demo purposes)

    Returns:
        Status message confirming logs were cleared
    """
    clear_logs()
    return {
        "status": "cleared",
        "message": "All telemetry logs have been cleared"
    }
