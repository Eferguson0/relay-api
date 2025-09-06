"""
RID (Resource ID) utilities for generating and parsing resource identifiers.
Format: <type>..<random-string>
"""

import secrets
import string
from typing import Optional


def generate_rid(resource_type: str, length: int = 12) -> str:
    """
    Generate a RID for a given resource type.

    Args:
        resource_type: The type of resource (e.g., 'user', 'diet', 'weight')
        length: Length of the random string (default: 12)

    Returns:
        RID in format: <type>..<random-string>
    """
    # Generate random string using letters and numbers
    alphabet = string.ascii_lowercase + string.digits
    random_string = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{resource_type}..{random_string}"


def parse_rid(rid: str) -> Optional[tuple[str, str]]:
    """
    Parse a RID into its components.

    Args:
        rid: The RID to parse

    Returns:
        Tuple of (resource_type, random_string) or None if invalid format
    """
    if not rid or ".." not in rid:
        return None

    parts = rid.split("..", 1)
    if len(parts) != 2:
        return None

    resource_type, random_string = parts
    if not resource_type or not random_string:
        return None

    return resource_type, random_string


def is_valid_rid(rid: str, expected_type: Optional[str] = None) -> bool:
    """
    Validate if a RID is in the correct format and optionally matches expected type.

    Args:
        rid: The RID to validate
        expected_type: Optional expected resource type

    Returns:
        True if valid, False otherwise
    """
    parsed = parse_rid(rid)
    if not parsed:
        return False

    resource_type, _ = parsed
    if expected_type and resource_type != expected_type:
        return False

    return True


# Common RID types
RID_TYPES = {
    "user": "user",
    "diet": "diet",
    "weight": "weight",
    "goal_weight": "goal_weight",
    "goal_daily_diet": "goal_daily_diet",
    "goal_message": "goal_message",
    "heart_rate": "heart_rate",
}
