"""
Tool: analyze_record
General mathematical and analytical tool.
1. Evaluates numeric records (compares bills to historical averages, flags anomalies).
2. Calculates exact trigger dates (e.g., event_date - 1 day) without LLM arithmetic errors.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import dateutil.parser

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def analyze_record(analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs deterministic calculations for bills, anomalies, and schedule triggers.

    Args:
        analysis_type (str): Either 'bill_anomaly' or 'schedule_trigger'.
        data (Dict[str, Any]):
            For 'bill_anomaly':
                - current_amount (float): The amount of the recent bill.
                - historical_amounts (List[float]): Past 3-6 bill amounts.
                - threshold_pct (float, optional): Anomaly threshold (default 15.0).
            For 'schedule_trigger':
                - event_datetime (str): ISO or human datetime of the event (e.g. '2026-10-15T15:00:00').
                - offset_days (int, optional): Days before event to fire reminder (default 1).
                - offset_hours (int, optional): Hours before event (default 0).

    Returns:
        Dict[str, Any]: Structured calculation results.
    """
    if analysis_type == "bill_anomaly":
        current = float(data.get("current_amount", 0.0))
        history = [float(x) for x in data.get("historical_amounts", [])]
        threshold = float(data.get("threshold_pct", 15.0))

        if not history:
            return {
                "success": False,
                "error": "No historical amounts provided for comparison."
            }

        avg = sum(history) / len(history)
        diff = current - avg
        pct_increase = (diff / avg) * 100 if avg > 0 else 0.0
        is_anomaly = pct_increase >= threshold

        return {
            "success": True,
            "analysis_type": "bill_anomaly",
            "current_amount": round(current, 2),
            "historical_average": round(avg, 2),
            "dollar_difference": round(diff, 2),
            "percentage_difference": round(pct_increase, 1),
            "anomaly_detected": is_anomaly,
            "threshold_applied": threshold,
            "explanation": (
                f"Bill of ${current:.2f} is {pct_increase:.1f}% higher than your historical "
                f"average of ${avg:.2f} (threshold: {threshold}%)."
                if is_anomaly else
                f"Bill of ${current:.2f} is within normal variation of your historical average of ${avg:.2f}."
            )
        }

    elif analysis_type == "schedule_trigger":
        event_str = data.get("event_datetime")
        offset_days = int(data.get("offset_days", 1))
        offset_hours = int(data.get("offset_hours", 0))

        if not event_str:
            return {
                "success": False,
                "error": "event_datetime is required."
            }

        try:
            event_dt = dateutil.parser.parse(event_str)
            trigger_dt = event_dt - timedelta(days=offset_days, hours=offset_hours)
            
            return {
                "success": True,
                "analysis_type": "schedule_trigger",
                "event_datetime": event_dt.isoformat(),
                "trigger_datetime": trigger_dt.isoformat(),
                "offset_days": offset_days,
                "offset_hours": offset_hours,
                "friendly_event": event_dt.strftime("%A, %B %d, %Y at %I:%M %p"),
                "friendly_trigger": trigger_dt.strftime("%A, %B %d, %Y at %I:%M %p"),
                "summary": f"Armed reminder set for {trigger_dt.strftime('%b %d at %I:%M %p')} ({offset_days} day before event)."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse datetime '{event_str}': {str(e)}"
            }

    return {
        "success": False,
        "error": f"Unknown analysis_type '{analysis_type}'. Supported: 'bill_anomaly', 'schedule_trigger'."
    }
