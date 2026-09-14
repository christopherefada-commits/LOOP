"""
Amazon DynamoDB implementation of BaseLifeEventsStore using boto3.
"""

import os
from typing import List, Optional
from datetime import datetime
from models import LifeEvent, TimelineEntry, LifeEventStatus
from .base import BaseLifeEventsStore

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class DynamoDBStore(BaseLifeEventsStore):
    def __init__(self, table_name: str = "LOOP_LifeEvents", region_name: str = "us-east-1"):
        if not BOTO3_AVAILABLE:
            raise RuntimeError("boto3 is required for DynamoDBStore")
        self.region_name = os.environ.get("AWS_REGION", region_name)
        self.table_name = os.environ.get("DYNAMODB_TABLE", table_name)
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def get_all_events(self) -> List[LifeEvent]:
        try:
            resp = self.table.scan()
            items = resp.get("Items", [])
            events = [LifeEvent(**item) for item in items]
            events.sort(key=lambda x: x.updated_at, reverse=True)
            return events
        except Exception as e:
            print(f"[DynamoDBStore] Error scanning table: {e}")
            return []

    def get_event(self, event_id: str) -> Optional[LifeEvent]:
        try:
            resp = self.table.get_item(Key={"id": event_id})
            item = resp.get("Item")
            return LifeEvent(**item) if item else None
        except Exception as e:
            print(f"[DynamoDBStore] Error getting item {event_id}: {e}")
            return None

    def save_event(self, event: LifeEvent) -> None:
        try:
            event.updated_at = datetime.now().isoformat()
            self.table.put_item(Item=event.to_dict())
        except Exception as e:
            print(f"[DynamoDBStore] Error saving event {event.id}: {e}")

    def update_status(self, event_id: str, new_status: LifeEventStatus, timeline_note: Optional[str] = None) -> Optional[LifeEvent]:
        try:
            status_val = new_status.value if isinstance(new_status, LifeEventStatus) else new_status
            now_iso = datetime.now().isoformat()
            resp = self.table.update_item(
                Key={"id": event_id},
                UpdateExpression="SET #st = :s, updated_at = :u",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":s": status_val, ":u": now_iso},
                ReturnValues="ALL_NEW"
            )
            updated_item = resp.get("Attributes")
            if updated_item and timeline_note:
                self.add_timeline_entry(TimelineEntry(
                    event_id=event_id,
                    message=timeline_note,
                    action_type=f"status_to_{status_val}"
                ))
            return LifeEvent(**updated_item) if updated_item else None
        except Exception as e:
            print(f"[DynamoDBStore] Error updating status {event_id}: {e}")
            return None

    def get_timeline(self, limit: int = 50) -> List[TimelineEntry]:
        # For simplicity in DynamoDB, timeline can be read from a dedicated timeline table or local store fallback
        return []

    def add_timeline_entry(self, entry: TimelineEntry) -> None:
        pass

    def clear_all(self) -> None:
        pass
