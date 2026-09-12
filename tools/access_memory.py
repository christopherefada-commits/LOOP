"""
Tool: access_memory
Queries the Life Events store for existing open loops and past records.
Enables the agent to correlate new documents (like a complaint email) to existing records (like a purchase receipt).
"""

from typing import List, Dict, Any, Optional
from store.factory import get_store
from models import LifeEventStatus

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def access_memory(query: str = "", filter_status: str = "all") -> List[Dict[str, Any]]:
    """
    Retrieves stored Life Events (Open Loops) from memory to check current obligations and past facts.

    Args:
        query (str): Optional search query to match against titles, summaries, or evidence (e.g. 'Sony', 'headphones', 'electricity').
        filter_status (str): Optional status filter ('all', 'active', 'awaiting_approval', 'completed').

    Returns:
        List[Dict[str, Any]]: List of matching Life Events currently in memory.
    """
    store = get_store()
    events = store.get_all_events()
    results = []

    for evt in events:
        if filter_status != "all":
            if filter_status == "active" and evt.status in (LifeEventStatus.COMPLETED, LifeEventStatus.DISMISSED):
                continue
            elif filter_status != "active" and evt.status.value != filter_status:
                continue

        if query:
            q_lower = query.lower()
            combined_text = f"{evt.title} {evt.summary} {evt.type.value} {' '.join(evt.evidence)}".lower()
            if q_lower not in combined_text:
                continue

        results.append(evt.to_dict())

    return results
