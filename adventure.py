"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
"""CSC111 Project 1: Text Adventure Game - Game Manager

Refactored for improved readability and structure.
"""

from __future__ import annotations
import json
from typing import Optional, Dict, List
from game_entities import Location, Item
from proj1_event_logger import Event, EventList

# Constants for location IDs
DORM_ID = 0
ROBARTS_1F = 3
LOST_AND_FOUND = 4
TRASH_CAN_ID = 6

# Constants for item names
TEXTBOOK = "textbook"
TOONIE = "toonie"
LOCKER_KEY = "locker key"
TRASH_ITEMS = {"waste-paper", "food-scraps", "waste bottles", "vegetable peelings"}

# Scoring rules (item: {location: points})
SCORING = {
    TEXTBOOK: {ROBARTS_1F: 2},
    TOONIE: {LOST_AND_FOUND: 5},
    **{item: {TRASH_CAN_ID: 1} for item in TRASH_ITEMS}
}

class AdventureGame:
    """A text adventure game manager handling game state and logic.

    Attributes:
        current_location_id: ID of player's current location
        ongoing: Game status flag
        score: Player's current score
        inventory: Items player is carrying
        event_log: History of game events
        trash_collected: Track collected trash items
        _locations: All game locations (id -> Location)
        _items: All game items
    """

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """Initialize game state from JSON data."""
        self._locations, self._items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True
        self.score = 0
        self.inventory = []
        self.event_log = EventList()
        self.trash_collected = {item: False for item in TRASH_ITEMS}

    @staticmethod
    def _load_game_data(filename: str) -> tuple[Dict[int, Location], List[Item]]:
        """Load game data from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        locations = {
            loc['id']: Location(
                loc['id'],
                loc['brief_description'],
                loc['long_description'],
                loc['available_commands'],
                loc['items']
            ) for loc in data['locations']
        }

        items = [
            Item(
                item['name'],
                item['start_position'],
                item['target_position'],
                item['target_points']
            ) for item in data['items']
        ]

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Get location by ID (current if None)."""
        target_id = loc_id if loc_id is not None else self.current_location_id
        return self._locations[target_id]

    def handle_command(self, command: str) -> None:
        """Process player command and update game state."""
        cmd = command.lower().strip()
        location = self.get_location()

        # Log command before processing
        self.event_log.add_event(Event(
            location.id_num,
            location.long_description,
            next_command=cmd
        ))

        if cmd == "look":
            self._handle_look(location)
        elif cmd == "inventory":
            self._handle_inventory()
        elif cmd == "score":
            self._handle_score()
        elif cmd == "undo":
            self._handle_undo()
        elif cmd == "log":
            self._handle_log()
        elif cmd == "quit":
            self._handle_quit()
        elif cmd.startswith("go "):
            self._handle_movement(cmd, location)
        elif cmd.startswith("pick up "):
            self._handle_pickup(cmd, location)
        elif cmd.startswith("drop "):
            self._handle_drop(cmd, location)
        else:
            print("Invalid command.")

    def _handle_look(self, location: Location) -> None:
        """Handle look command."""
        print(location.long_description if not location.visited else location.brief_description)
        location.visited = True

    def _handle_inventory(self) -> None:
        """Show player inventory."""
        print("Inventory:", self.inventory if self.inventory else "Empty")

    def _handle_score(self) -> None:
        """Display current score."""
        print(f"Current score: {self.score}")

    def _handle_undo(self) -> None:
        """Revert last action."""
        if not self.event_log.is_empty():
            last_event = self.event_log.remove_last_event()
            self._reverse_event(last_event)
            print("Undid:", last_event.next_command)
        else:
            print("Nothing to undo.")

    def _handle_log(self) -> None:
        """Display event history."""
        self.event_log.display_events()

    def _handle_quit(self) -> None:
        """End game session."""
        self.ongoing = False
        print("Thanks for playing!")

    def _handle_movement(self, command: str, current_loc: Location) -> None:
        """Process movement commands."""
        direction = command.split(maxsplit=1)[1]
        target_id = current_loc.available_commands.get(direction)

        if target_id is None:
            print("Can't go that way.")
            return

        target_loc = self.get_location(target_id)
        if target_loc.locked and not self._unlock_location(target_loc):
            return

        self.current_location_id = target_id
        print(f"Moved {direction} to {target_loc.brief_description}")

    def _unlock_location(self, location: Location) -> bool:
        """Attempt to unlock a locked location."""
        if LOCKER_KEY in self.inventory:
            location.locked = False
            print("Used locker key to unlock!")
            return True
        print("This area is locked. Find a key!")
        return False

    def _handle_pickup(self, command: str, location: Location) -> None:
        """Process item pickup."""
        item_name = command.split("pick up ", 1)[1]
        if item_name in location.items:
            self.inventory.append(item_name)
            location.items.remove(item_name)
            print(f"Picked up {item_name}!")
        else:
            print(f"{item_name} not found here.")

    def _handle_drop(self, command: str, location: Location) -> None:
        """Process item drop."""
        item_name = command.split("drop ", 1)[1]
        if item_name not in self.inventory:
            print(f"Not carrying {item_name}.")
            return

        self.inventory.remove(item_name)
        location.items.append(item_name)
        print(f"Dropped {item_name}.")

        # Update scoring and check for special conditions
        self._update_score(item_name, location.id_num)
        self._check_trash_disposal(item_name, location.id_num)
        self._check_key_unlock()

    def _update_score(self, item: str, location_id: int) -> None:
        """Update score based on item and location."""
        points = SCORING.get(item, {}).get(location_id, 0)
        if points > 0:
            self.score += points
            print(f"+{points} points! Total: {self.score}")

    def _check_trash_disposal(self, item: str, location_id: int) -> None:
        """Track trash items disposed in correct location."""
        if location_id == TRASH_CAN_ID and item in TRASH_ITEMS:
            self.trash_collected[item] = True

    def _check_key_unlock(self) -> None:
        """Check if all trash collected and award key."""
        if all(self.trash_collected.values()):
            dorm = self.get_location(DORM_ID)
            if LOCKER_KEY not in self.inventory:
                self.inventory.append(LOCKER_KEY)
                print("A locker key appeared in your inventory!")

    def _reverse_event(self, event: Event) -> None:
        """Reverse actions from given event."""
        cmd = event.next_command
        current_loc = self.get_location()

        if cmd.startswith("pick up "):
            item = cmd.split("pick up ", 1)[1]
            if item in self.inventory:
                self.inventory.remove(item)
                current_loc.items.append(item)
        elif cmd.startswith("drop "):
            item = cmd.split("drop ", 1)[1]
            if item in current_loc.items:
                current_loc.items.remove(item)
                self.inventory.append(item)
        elif cmd.startswith("go "):
            self.current_location_id = event.location_id

    def check_win_condition(self) -> bool:
        """Check if player has met win conditions."""
        required_items = {"laptop charger", "USB drive", "UofT mug"}
        return (
            all(item in self.inventory for item in required_items)
            and self.score >= 10
        )

if __name__ == "__main__":
    game = AdventureGame('game_data.json', DORM_ID)
    
    while game.ongoing:
        current_loc = game.get_location()
        
        # Display location info
        if not current_loc.visited:
            print(f"\nLOCATION {current_loc.id_num}\n{current_loc.long_description}")
            current_loc.visited = True
        else:
            print(f"\nLOCATION {current_loc.id_num}\n{current_loc.brief_description}")
        
        # Show available actions
        print("\nAvailable actions:", list(current_loc.available_commands.keys()) + ["look", "inventory", "score", "undo", "log", "quit"])
        
        # Get player input
        command = input("\nEnter command: ").strip()
        
        # Process command
        game.handle_command(command)
        
        # Check win condition
        if game.check_win_condition():
            print("\n=== YOU WIN! ===")
            print("Collected all required items with sufficient score!")
            game.ongoing = False

