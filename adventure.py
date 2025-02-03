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

from __future__ import annotations
import json
from typing import Optional, Dict, List
from game_entities import Location, Item
from proj1_event_logger import Event, EventList


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: the ID of the location the game is currently in
        - ongoing: whether the game is ongoing
        - score: the player's current score
        - inventory: the items the player is currently carrying
        - event_log: a list of events that have occurred in the game
        - trash_collected: A mapping recording whether the trash in dorm has been picked up.


    Representation Invariants:
        - current_location_id in _locations
        - score >= 0
    """
    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed
    score: int
    inventory: list[str]
    event_log: EventList
    trash_collected: dict[str, bool]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        self._locations, self._items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True
        self.score = 0
        self.inventory = []
        self.event_log = EventList()
        self.trash_collected = {
            "waste-paper": False,
            "food-scraps": False,
            "waste bottles": False,
            "vegetable peelings": False
        }

    @staticmethod
    def _load_game_data(filename: str) -> tuple[Dict[int, Location], List[Item]]:
        """Load game data with proper command parsing"""
        with open(filename, 'r') as f:
            data = json.load(f)

        locations = {}
        for loc_data in data['locations']:
            # Filter only movement commands
            available_commands = {}
            for cmd, target_id in loc_data['available_commands'].items():
                if cmd.startswith("go "):
                    direction = cmd.split(" ", 1)[1]  # Extract direction part
                    available_commands[direction] = target_id

            locations[loc_data['id']] = Location(
                loc_data['id'],
                loc_data['brief_description'],
                loc_data['long_description'],
                available_commands,
                loc_data['items'],
                loc_data.get('requires_key', False),
                loc_data.get('locked', False)
            )

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
        """Get current or specified location"""
        target_id = loc_id if loc_id is not None else self.current_location_id
        return self._locations[target_id]

    def handle_command(self, command: str) -> None:
        """Process player command with proper item/location handling"""
        cmd = command.strip().lower()
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
        if not self.event_log.is_empty():
            last_event = self.event_log.remove_last_event()
            print(f"Undid last action: {last_event}")
        else:
            print("No action to undo.")

    def _handle_log(self) -> None:
        """Display event history."""
        self.event_log.display_events()

    def _handle_quit(self) -> None:
        """End game session."""
        self.ongoing = False
        print("Thanks for playing!")

    def _handle_movement(self, command: str, current_loc: Location) -> None:
        """Process movement commands from formatted game data"""
        direction = command.split(" ", 1)[1]
        target_id = current_loc.available_commands.get(direction)

        if target_id is None:
            print("Can't go that way.")
            return

        target_loc = self.get_location(target_id)
        if target_loc.locked:
            if not self._check_unlock_condition(target_loc):
                print("This location is locked. You can't go there yet.")
                return
            else:
                target_loc.locked = False
                print(f"The {target_loc.id_num} is now unlocked!")

        self.current_location_id = target_id
        print(f"Moved {direction} to {target_loc.brief_description}")

    def _check_unlock_condition(self) -> bool:
        """Check if the location is unlocked based on certain conditions"""
        if "key" in self.inventory:
            return True
        else:
            return False

    def _handle_pickup(self, command: str, location: Location) -> None:
        """Process item pickup with exact name matching"""
        item_name = command.split("pick up ", 1)[1].strip()

        # Handle case-sensitive matching from JSON
        actual_name = next((item for item in location.items if item.lower() == item_name.lower()), None)

        if actual_name:
            self.inventory.append(actual_name)
            location.items.remove(actual_name)
            print(f"Picked up {actual_name}!")
        else:
            print(f"{item_name} not found here.")

    def _handle_drop(self, command: str, location: Location) -> None:
        """Process item drop with exact name matching"""
        item_name = command.split("drop ", 1)[1].strip()

        # Find case-sensitive match in inventory
        actual_name = next((item for item in self.inventory if item.lower() == item_name.lower()), None)

        if not actual_name:
            print(f"Not carrying {item_name}.")
            return

        self.inventory.remove(actual_name)
        location.items.append(actual_name)
        print(f"Dropped {actual_name}.")

        # Update scoring and check for special conditions
        self._update_score(actual_name, location.id_num)
        self._check_trash_disposal(actual_name, location.id_num)
        self._check_key_unlock()

    def _update_score(self, item: str, location_id: int) -> None:
        """Update score based on exact item/location matches"""
        if item == "textbook" and location_id == 3:  # Robarts Library 1F
            self.score += 2
        elif item == "toonie" and location_id == 4:  # the lost and found office
            self.score += 5
        elif item in self.trash_collected and location_id == 6:  # Trash can
            self.score += 1

    def _check_trash_disposal(self, item: str, location_id: int) -> None:
        """Track trash items disposed in correct location"""
        if location_id == 6 and item in self.trash_collected:
            self.trash_collected[item] = True

    def _check_key_unlock(self) -> None:
        """Check if all trash collected and award key"""
        if all(self.trash_collected.values()):
            if "locker key" not in self.inventory:
                self.inventory.append("locker key")
                print("A locker key falls out of the trash can! You pick it up automatically.")

    def check_win_condition(self) -> bool:
        """Check win state with exact item names"""
        required_items = {"laptop charger", "USB Drive", "UofT mug"}
        return all(item in self.inventory for item in required_items) and self.score >= 10


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    game = AdventureGame('game_data.json', 0)  # Start at dorm (ID 0)

    while game.ongoing:
        current_loc = game.get_location()
        if not current_loc.visited:
            print(f"\nLOCATION {current_loc.id_num}\n{current_loc.long_description}")
            current_loc.visited = True
        else:
            print(f"\nLOCATION {current_loc.id_num}\n{current_loc.brief_description}")

        # Show available actions
        print("\nAvailable actions:")
        print("- " + "\n- ".join(current_loc.available_commands.keys()))
        print("- look\n- inventory\n- score\n- undo\n- log\n- quit")
        if current_loc.items:
            print("- pick up " + "\n- pick up ".join(current_loc.items))

        command = input("\nEnter command: ").strip()

        game.handle_command(command)

        if game.check_win_condition():
            print("\n=== YOU WIN! ===")
            print("Collected all required items with sufficient score!")
            game.ongoing = False


