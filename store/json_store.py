"""
Local JSON implementation of BaseLifeEventsStore.
Ensures zero-dependency instant execution and offline presentation reliability.
"""

import json
import os
import threading
from typing import List, Optional
from datetime import datetime
from models import LifeEvent, TimelineEntry, LifeEventStatus
from .base import BaseLifeEventsStore


class LocalJsonStore(BaseLifeEventsStore):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.events_file = os.path.join(data_dir, "life_events.json")
        self.timeline_file = os.path.join(data_dir, "timeline.json")
        self._lock = threading.Lock()
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.events_file):
            with open(self.events_file, "w") as f:
                json.dump([], f, indent=2)
        if not os.path.exists(self.timeline_file):
            with open(self.timeline_file, "w") as f:
                json.dump([], f, indent=2)

    def _read_events_raw(self) -> List[dict]:
        try:
            with open(self.events_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_events_raw(self, events: List[dict]):
        with open(self.events_file, "w") as f:
            json.dump(events, f, indent=2)

    def _read_timeline_raw(self) -> List[dict]:
        try:
            with open(self.timeline_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_timeline_raw(self, entries: List[dict]):
        with open(self.timeline_file, "w") as f:
            json.dump(entries, f, indent=2)

    def get_all_events(self) -> List[LifeEvent]:
        with self._lock:
            raw = self._read_events_raw()
            events = [LifeEvent(**item) for item in raw]
            events.sort(key=lambda x: x.updated_at, reverse=True)
            return events

    def get_event(self, event_id: str) -> Optional[LifeEvent]:
        with self._lock:
            raw = self._read_events_raw()
            for item in raw:
                if item.get("id") == event_id:
                    return LifeEvent(**item)
            return None

    def save_event(self, event: LifeEvent) -> None:
        with self._lock:
            event.updated_at = datetime.now().isoformat()
            raw = self._read_events_raw()
            found = False
            for i, item in enumerate(raw):
                if item.get("id") == event.id:
                    raw[i] = event.to_dict()
                    found = True
                    break
            if not found:
                raw.append(event.to_dict())
            self._write_events_raw(raw)

    def update_status(self, event_id: str, new_status: LifeEventStatus, timeline_note: Optional[str] = None) -> Optional[LifeEvent]:
        with self._lock:
            raw = self._read_events_raw()
            updated_event = None
            for i, item in enumerate(raw):
                if item.get("id") == event_id:
                    item["status"] = new_status.value if isinstance(new_status, LifeEventStatus) else new_status
                    item["updated_at"] = datetime.now().isoformat()
                    updated_event = LifeEvent(**item)
                    raw[i] = item
                    break
            if updated_event:
                self._write_events_raw(raw)
                if timeline_note:
                    entry = TimelineEntry(
                        event_id=event_id,
                        message=timeline_note,
                        action_type=f"status_to_{new_status.value if isinstance(new_status, LifeEventStatus) else new_status}"
                    )
                    t_raw = self._read_timeline_raw()
                    t_raw.insert(0, entry.to_dict())
                    self._write_timeline_raw(t_raw)
            return updated_event

    def get_timeline(self, limit: int = 50) -> List[TimelineEntry]:
        with self._lock:
            raw = self._read_timeline_raw()
            entries = [TimelineEntry(**item) for item in raw]
            return entries[:limit]

    def add_timeline_entry(self, entry: TimelineEntry) -> None:
        with self._lock:
            raw = self._read_timeline_raw()
            raw.insert(0, entry.to_dict())
            self._write_timeline_raw(raw)

    def clear_all(self) -> None:
        with self._lock:
            self._write_events_raw([])
            self._write_timeline_raw([])
