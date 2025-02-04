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
from typing import Optional
from game_entities import Location, Item
from proj1_event_logger import Event, EventList, UndoSystem


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: the ID of the location the game is currently in
        - ongoing: whether the game is ongoing
        - score: the player's current score
        - inventory: the items the player is currently carrying
        - event_log: a list of events that have occurred in the game


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
    current_location_id: int
    ongoing: bool
    score: int
    inventory: list[str]
    event_log: EventList

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """Initialize a new text adventure game."""
        self._locations, self._items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True
        self.score = 0
        self.inventory = []
        self.event_log = EventList()
        self.undo_system = UndoSystem()  # Create UndoSystem instance
        self.undo_stack = []  # Additional stack to properly track previous states

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        locations = {}
        for loc_data in data['locations']:
            location_obj = Location(
                loc_data['id'],
                loc_data['brief_description'],
                loc_data['long_description'],
                loc_data['available_commands'],
                loc_data['items']
            )
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:
            item_obj = Item(
                item_data['name'],
                item_data['description'],
                item_data['start_position'],
                item_data['target_position'],
                item_data['target_points']
            )
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID."""
        if loc_id is None:
            loc_id = self.current_location_id
        return self._locations[loc_id]

    def go(self, direction: str) -> None:
        """Move the player in the specified direction.

        Precondition:
            - direction in ["north", "south", "west", "east]

        """
        self._save_state()

        current_location = self.get_location()
        command = f"go {direction}"
        if command in current_location.available_commands:
            target_id = current_location.available_commands[command]
            # if the target location is the reading room but the player's current scores are lower than 20, can't go in.
            if target_id == 7 and self.score < 20:
                print("You need at least 20 points to enter the reading room.")
            else:
                self.current_location_id = target_id
        else:
            print("You can't go that way.")

    def pick_up(self, item_name: str) -> None:
        """Pick up an item from the current location."""
        self._save_state()

        current_location = self.get_location()
        found_item = None
        for item in current_location.items:
            if item.lower() == item_name.lower():
                found_item = item
                break

        if found_item:
            self.inventory.append(found_item)
            current_location.items.remove(found_item)
            print(f"You picked up the {found_item}.")
        else:
            print(f"There is no {item_name} here.")

    def drop(self, item_name: str) -> None:
        """Drop an item in the current location."""
        self._save_state()

        found_item = None
        for inv_item in self.inventory:
            if inv_item.lower() == item_name.lower():
                found_item = inv_item
                break
        if found_item:
            current_loc = self.get_location()
            if current_loc.items is None:
                current_loc.items = []
            current_loc.items.append(found_item)
            self.inventory.remove(found_item)
            print(f"You dropped the {found_item}.")
            self._check_item_delivery(found_item)
            self.check_victory()
        else:
            print(f"You don't have a {item_name}.")

    def _check_item_delivery(self, item_name: str) -> None:
        """Check if an item has been delivered to its target location."""
        for item in self._items:
            if item.name == item_name and self.current_location_id == item.target_position:
                self.score += item.target_points
                print(f"You earned {item.target_points} points!")

    def check_victory(self) -> None:
        """Check if the player wins by dropping all required items at the dorm."""
        required_items = {"USB Drive", "laptop charger", "UofT mug"}
        dorm = self.get_location(0)  # Assuming dorm is location ID 0
        if all(item in dorm.items for item in required_items):
            print("Congratulations! You have dropped all required items in the dorm and can now finish your project!")
            self.ongoing = False

    def look(self) -> None:
        """Display the description of the current location."""
        current_location = self.get_location()
        if current_location.visited:
            print(current_location.brief_description)
        else:
            print(current_location.long_description)
            current_location.visited = True

    def display_inventory(self) -> None:
        """Display the player's inventory."""
        if self.inventory:
            print("Inventory:")
            for item in self.inventory:
                print(f"- {item}")
        else:
            print("Your inventory is empty.")

    def update_score(self, item: str, location_id: int) -> None:
        """Update score based on exact item and location"""
        if item == "textbook" and location_id == 3:  # Robarts Library 1F
            self.score += 5
        elif item == "toonie" and location_id == 4:  # the lost and found office
            self.score += 5
        elif item in ["waste paper", "food scraps", "waste bottles", "vegetable peelings"] and location_id == 6:
            self.score += 2

    def display_score(self) -> None:
        """Display the player's current score."""
        print(f"Your current score is: {self.score}")

    def _save_state(self) -> None:
        """Save the current game state for undo functionality."""
        self.undo_stack.append({
            "current_location_id": self.current_location_id,
            "inventory": self.inventory[:],  # Copy list
            "score": self.score
        })

    def undo(self) -> None:
        """Restore the previous game state from the undo stack."""
        if self.undo_stack:
            prev_state = self.undo_stack.pop()
            self.current_location_id = prev_state["current_location_id"]
            self.inventory = prev_state["inventory"][:]
            self.score = prev_state["score"]
            print("Previous action undone.")
        else:
            print("Nothing to undo!")

    def log(self) -> None:
        """Display the event log."""
        self.event_log.display_events()

    def quit(self) -> None:
        """Quit the game."""
        print("Goodbye.")
        self.ongoing = False


if __name__ == "__main__":

    game = AdventureGame('game_data.json', 0)
    game_log = EventList()
    menu = ["look", "inventory", "score", "undo", "log", "quit"]

    while game.ongoing:
        current_location = game.get_location()
        print("\n" + current_location.brief_description)
        print("What to do? Choose from: look, inventory, score, undo, log, quit")
        print("At this location, you can also:")
        for action in current_location.available_commands:
            print(f"- {action}")

        choice = input("\nEnter action: ").lower().strip()

        if choice == "look":
            game.look()
        elif choice == "inventory":
            game.display_inventory()
        elif choice == "score":
            game.display_score()
        elif choice == "undo":
            game.undo()
        elif choice == "log":
            game.log()
        elif choice == "quit":
            game.quit()
        elif choice.startswith("go "):
            direction = choice.split(" ")[1]
            game.go(direction)
        elif choice.startswith("pick up "):
            item_name = choice.split("pick up ", 1)[1]
            game.pick_up(item_name)
        elif choice.startswith("drop "):
            item_name = choice.split("drop ", 1)[1]
            game.drop(item_name)
        else:
            print("Invalid command. Try again.")
