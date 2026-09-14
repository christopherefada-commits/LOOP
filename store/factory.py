"""
Store factory: Returns the active store backend.
Defaults to LocalJsonStore for immediate local execution and offline demos.
"""

import os
from .base import BaseLifeEventsStore
from .json_store import LocalJsonStore


def get_store() -> BaseLifeEventsStore:
    use_dynamo = os.environ.get("USE_DYNAMODB", "false").lower() in ("true", "1", "yes")
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
    
    if use_dynamo and aws_key:
        try:
            from .dynamo_store import DynamoDBStore
            return DynamoDBStore()
        except Exception as e:
            print(f"[StoreFactory] Could not connect to DynamoDB ({e}). Falling back to LocalJsonStore.")
            return LocalJsonStore()
    
    return LocalJsonStore()
