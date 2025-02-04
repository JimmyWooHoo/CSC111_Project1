"""CSC111 Project 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

You can copy/paste your code from the ex1_simulation file into this one, and modify it as needed
to work with your game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of this event's location
    - description: Long description of this event's location
    - next_command: String command which leads this event to the next event, None if this is the last game event
    - next: Event object representing the next event in the game, or None if this is the last game event
    - prev: Event object representing the previous event in the game, None if this is the first game event
    """

    # NOTES:
    # This is proj1_event_logger (separate from the ex1 file). In this file, you may add new attributes/methods,
    # or modify the names or types of provided attributes/methods, as needed for your game.
    # If you want to create a special type of Event for your game that requires a different
    # set of attributes, you can create new classes using inheritance, as well.

    id_num: int
    description: str
    next_command: Optional[str] = None
    next: Optional[Event] = None
    prev: Optional[Event] = None


class EventList:
    """
    A linked list of game events.

    Instance Attributes:
        - first: The first event in the event list, or None if the list is empty.
        - last: The last event in the event list, or None if the list is empty.

    Representation Invariants:
        - If the list is empty, then first and last must be None.
        - If the list is not empty, then first and last must not be None.
        - If the list only has one event, the first and last refer to the same event.
    """
    first: Optional[Event]
    last: Optional[Event]

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def display_events(self) -> None:
        """Display all events in chronological order."""
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}")
            curr = curr.next

    def is_empty(self) -> bool:
        """Return whether this event list is empty."""

        return self.first is None

    def add_event(self, event: Event, command: str = None) -> None:
        """Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.
        """
        # Hint: You should update the previous node's <next_command> as needed

        if self.is_empty():
            self.first = event
        else:
            self.last.next = event
            self.last.next_command = command
            event.prev = self.last
        self.last = event

    def remove_last_event(self) -> Optional[Event]:
        """Remove the last event from this event list.
        If the list is empty, do nothing."""

        # Hint: The <next_command> and <next> attributes for the new last event should be updated as needed

        if self.is_empty():
            return None
        elif self.first == self.last:
            item = self.first
            self.first = None
            self.last = None
            return item
        else:
            last_event = self.last
            self.last = self.last.prev
            self.last.next = None
            self.last.next_command = None
            return last_event

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence."""

        id_log = []
        curr = self.first
        while curr is not None:
            id_log.append(curr.id_num)
            curr = curr.next
        return id_log

    # Note: You may add other methods to this class as needed


class UndoSystem:
    """
    A class that manages the undo functionality in the adventure game.

    This system keeps track of past game states using a stack data structure.
    Players can revert their most recent action by using the 'undo' command.
    """

    def __init__(self):
        """
        Initialize an empty undo stack.

        The stack stores previous game states, allowing players to revert
        their last move when needed.
        """
        self.undo_stack = []

    def save_state(self, game_state: dict):
        """
        Save a copy of the current game state before an action is performed.

        This function should be called before any significant state-changing
        action (e.g., moving, picking up/dropping an item) to allow undoing it.

        :param game_state: A dictionary representing the current game state.
        """
        self.undo_stack.append(game_state.copy())

    def undo(self):
        """
        Revert the game to the last saved state.

        This function restores the most recent state from the undo stack.
        If no previous state exists, it prints a message indicating that undo
        is not possible.

        :return: The previous game state dictionary if available, otherwise None.
        """
        if self.undo_stack:
            return self.undo_stack.pop()
        else:
            print("Nothing to undo!")
            return None



if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
