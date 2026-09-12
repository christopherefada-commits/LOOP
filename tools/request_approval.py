"""
Tool: request_approval
Strands Human-in-the-Loop checkpoint.
Pauses autonomous execution before high-impact actions (submitting claims, paying bills, dispatching forms).
Transitions Life Event to 'awaiting_approval'.
"""

from typing import Dict, Any, List
from store.factory import get_store
from models import LifeEventStatus, TimelineEntry

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def request_approval(event_id: str, action_summary: str, evidence_summary: str) -> Dict[str, Any]:
    """
    Strands Human-in-the-Loop checkpoint.
    Pauses execution before performing any high-impact external action and requests user authorization.

    Args:
        event_id (str): The ID of the Life Event awaiting user decision.
        action_summary (str): Plain-language summary of what will happen upon approval (e.g. 'Submit warranty replacement claim for Sony Headphones').
        evidence_summary (str): Summary of evidence verified (e.g. 'Verified purchase receipt, 1-year warranty coverage, and fault description').

    Returns:
        Dict[str, Any]: Checkpoint status and approval token.
    """
    store = get_store()
    event = store.get_event(event_id)

    if not event:
        return {
            "success": False,
            "error": f"LifeEvent '{event_id}' not found in store."
        }

    # Transition status to awaiting_approval
    event.status = LifeEventStatus.AWAITING_APPROVAL
    store.save_event(event)

    # Log conversational timeline entry
    note = f"Awaiting your review: {action_summary}"
    store.add_timeline_entry(TimelineEntry(
        event_id=event_id,
        message=note,
        action_type="request_approval"
    ))

    return {
        "status": "awaiting_approval",
        "event_id": event_id,
        "action_summary": action_summary,
        "evidence_summary": evidence_summary,
        "message": "Execution paused. Awaiting user approval on dashboard."
    }
