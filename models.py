"""
LOOP — Data Models
Defines LifeEvent, TimelineEntry, and associated enums.
Adheres to the specification: 'Documents are evidence, Life Events are what the agent actually reasons about.'
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class LifeEventType(str, Enum):
    WARRANTY = "warranty"
    BILL = "bill"
    APPOINTMENT = "appointment"
    SUBMISSION = "submission"
    SUBSCRIPTION = "subscription"


class LifeEventStatus(str, Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    PREPARED = "prepared"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class LifeEventCategory(str, Enum):
    MONEY_RECOVER = "money_recover"    # Accent: Amber (#B8863B)
    MONEY_LOSE = "money_lose"          # Accent: Rust (#B54A2A)
    DEADLINE = "deadline"              # Accent: Loop Green (#1F5C45)
    SUBMISSION = "submission"          # Accent: Loop Green (#1F5C45)


class LifeEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    type: LifeEventType
    title: str
    summary: str
    status: LifeEventStatus = LifeEventStatus.DETECTED
    category: LifeEventCategory
    dollar_amount: Optional[float] = None
    due_or_event_date: Optional[str] = None
    trigger_date: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    prepared_action: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class TimelineEntry(BaseModel):
    id: str = Field(default_factory=lambda: f"tl_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%I:%M %p"))
    iso_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_id: Optional[str] = ""
    message: str
    action_type: str = "status_change"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
