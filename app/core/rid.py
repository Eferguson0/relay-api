"""
RID (Resource ID) utilities for generating and parsing resource identifiers.
Format: <high-level-type>..<type>.<random-string>
"""

import secrets
import string
from typing import Optional


def generate_rid(high_level_type: str, resource_type: str, length: int = 12) -> str:
    """
    Generate a RID for a given resource type.

    Args:
        high_level_type: The high-level category (e.g., 'auth', 'metric', 'goal', 'nutrition')
        resource_type: The specific resource type (e.g., 'user', 'diet', 'weight')
        length: Length of the random string (default: 12)

    Returns:
        RID in format: <high-level-type>..<type>.<random-string>
    """
    # Generate random string using letters and numbers
    alphabet = string.ascii_lowercase + string.digits
    random_string = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{high_level_type}..{resource_type}.{random_string}"


def parse_rid(rid: str) -> Optional[tuple[str, str, str]]:
    """
    Parse a RID into its components.

    Args:
        rid: The RID to parse

    Returns:
        Tuple of (high_level_type, resource_type, random_string) or None if invalid format
    """
    if not rid or ".." not in rid or "." not in rid:
        return None

    # Split by ".." first to get high_level_type and the rest
    parts = rid.split("..", 1)
    if len(parts) != 2:
        return None

    high_level_type, rest = parts

    # Split the rest by "." to get resource_type and random_string
    rest_parts = rest.split(".", 1)
    if len(rest_parts) != 2:
        return None

    resource_type, random_string = rest_parts

    if not high_level_type or not resource_type or not random_string:
        return None

    return high_level_type, resource_type, random_string


def is_valid_rid(
    rid: str,
    expected_high_level_type: Optional[str] = None,
    expected_type: Optional[str] = None,
) -> bool:
    """
    Validate if a RID is in the correct format and optionally matches expected types.

    Args:
        rid: The RID to validate
        expected_high_level_type: Optional expected high-level type
        expected_type: Optional expected resource type

    Returns:
        True if valid, False otherwise
    """
    parsed = parse_rid(rid)
    if not parsed:
        return False

    high_level_type, resource_type, _ = parsed
    if expected_high_level_type and high_level_type != expected_high_level_type:
        return False
    if expected_type and resource_type != expected_type:
        return False

    return True


# Common RID types organized by high-level categories
RID_TYPES = {
    # Auth
    "auth": {
        "user": "user",
    },
    # Goals
    "goal": {
        "general": "general",
        "weight": "weight",
        "macros": "macros",
    },
    # Metrics
    "metric": {
        "body_composition": "body_composition",
        "heart_rate": "heart_rate",
        "steps": "steps",
        "miles": "miles",
        "workouts": "workouts",
        "active_calories": "active_calories",
        "baseline_calories": "baseline_calories",
        "sleep": "sleep",
    },
    # Nutrition
    "nutrition": {
        "macros": "macros",
    },
}
