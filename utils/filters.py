# utils/filters.py
import json

def format_number(value):
    """Format number with commas"""
    if value is None:
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)

def from_json(value):
    """Convert JSON string to Python object"""
    if value is None or value == '':
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

# Export all filters
filters = {
    'format_number': format_number,
    'fromjson': from_json
}