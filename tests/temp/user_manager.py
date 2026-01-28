"""Simple user manager used by tests.

Edits add docstrings and initialize internal state; behavior remains
compatible with existing test expectations.
"""

from typing import List, Dict, Any, Optional


class UserManager:
    """Manage an in-memory list of user dicts (with 'name' and 'age')."""

    def __init__(self) -> None:
        """Initialize the user manager with an empty users list."""
        self.users: List[Dict[str, Any]] = []

    def add_user(self, name: str, age: int) -> None:
        """Add a new user to the list."""
        self.users.append({"name": name, "age": age})

    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Return the first user matching name (case-insensitive)."""
        for user in self.users:
            if user["name"].lower() == name.lower():
                return user

    def get_average_age(self) -> float:
        """Return the average age of all users."""
        total = 0
        for user in self.users:
            total += user["age"]
        return total / len(self.users)

    def remove_user(self, name: str) -> bool:
        """Remove the first user with the given name. Return True if removed."""
        for user in self.users:
            if user["name"] == name:
                self.users.remove(user)
                return True
        return False
