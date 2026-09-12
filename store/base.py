"""
Abstract base store interface for LOOP Life Events and Timeline entries.
Allows seamless switching between local JSON file storage and AWS DynamoDB.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from models import LifeEvent, TimelineEntry, LifeEventStatus


class BaseLifeEventsStore(ABC):

    @abstractmethod
    def get_all_events(self) -> List[LifeEvent]:
        """Returns all Life Events sorted by updated_at descending."""
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[LifeEvent]:
        """Returns a single Life Event by its ID, or None if not found."""
        pass

    @abstractmethod
    def save_event(self, event: LifeEvent) -> None:
        """Saves or updates a Life Event."""
        pass

    @abstractmethod
    def update_status(self, event_id: str, new_status: LifeEventStatus, timeline_note: Optional[str] = None) -> Optional[LifeEvent]:
        """Updates the status of a Life Event and optionally appends a timeline entry."""
        pass

    @abstractmethod
    def get_timeline(self, limit: int = 50) -> List[TimelineEntry]:
        """Returns chronological list of timeline entries."""
        pass

    @abstractmethod
    def add_timeline_entry(self, entry: TimelineEntry) -> None:
        """Appends a new timeline entry."""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Resets the store (useful for clean demo resets)."""
        pass
