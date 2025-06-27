#!/usr/bin/env python3
"""
Utility to clean datetime objects from event data before JSON serialization
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Union

def sanitize_datetime_objects(obj: Any) -> Any:
    """
    Recursively convert datetime objects to ISO format strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: sanitize_datetime_objects(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_datetime_objects(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_datetime_objects(item) for item in obj)
    else:
        return obj

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize object to JSON, converting datetime objects automatically
    """
    sanitized_obj = sanitize_datetime_objects(obj)
    return json.dumps(sanitized_obj, **kwargs)

class DateTimeEncoder(json.JSONEncoder):
    """Enhanced JSON encoder that handles datetime and other non-serializable objects"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            # Handle custom objects by converting to dict
            return sanitize_datetime_objects(obj.__dict__)
        elif hasattr(obj, 'to_dict'):
            # Handle objects with to_dict method
            return sanitize_datetime_objects(obj.to_dict())
        else:
            # Let the base class default method raise the TypeError
            return super().default(obj)
