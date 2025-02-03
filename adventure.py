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
from proj1_event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


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
    trash_collected: dict[str,bool]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing
        self.score = 0
        self.inventory = []
        self.event_log = EventList()
        self.trash_collected = {
            "waste-paper": False,
            "food-scraps": False,
            "waste bottles": False,
            "vegetable peelings": False}

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:
            item_obj = Item(item_data['name'], item_data['start_position'], item_data['target_position'],
                            item_data['target_points'])
            items += [item_obj]

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        if not loc_id:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def _update_score(self, item_name: str, location_id: int) -> None:
        """Update the player's score based on the item dropped and the location."""
        if item_name == "textbook" and location_id == 3:  # Robarts Library 1F
            self.score += 2
        elif item_name == "toonie" and location_id == 4:  # the lost and found office
            self.score += 5
        elif item_name in ["waste-paper", "food-scraps", "waste bottles",
                           "vegetable peelings"] and location_id == 6:  # trash can
            self.score += 1

    def handle_command(self, command: str) -> None:
        """Handle the given command and update the game state accordingly."""
        location = self.get_location()

        if command == "look":
            if location.visited is False:
                print(location.long_description)
            else:
                print(location.brief_description)
            location.visited = True
        elif command == "inventory":
            print("Inventory:", self.inventory)
        elif command == "score":
            print("Your current score is:", self.score)
        elif command == "undo":
            self._undo_last_action()
        elif command == "log":
            self.event_log.display_events()
        elif command == "quit":
            self.ongoing = False
            print("Goodbye!")
        elif command.startswith("go"):
            direction = command.split(" ")[1]
            if direction in location.available_commands:
                target_id = location.available_commands[direction]
                target_loc = self._locations[target_id]

                if target_loc.requires_key and target_loc.locked:
                    if "locker key" in self.inventory:
                        target_loc.locked = False
                        print("You unlocked the locker with your key!")
                    else:
                        print("This area is locked. You need a key to enter.")
                        return

                self.current_location_id = target_id
                print(f"You moved {direction} to {target_loc.brief_description}")
            else:
                print("You can't go that way.")
        elif command.startswith("pick up"):
            item_name = command.split("pick up ")[1]
            if item_name in location.items:
                self.inventory.append(item_name)
                location.items.remove(item_name)
                print(f"You picked up the {item_name}.")
            else:
                print(f"There is no {item_name} here.")
        elif command.startswith("drop"):
            item_name = command.split("drop ")[1]
            if item_name in self.inventory:
                self.inventory.remove(item_name)
                location.items.append(item_name)
                print(f"You dropped the {item_name}.")
                if location.id_num == 6 and item_name in self.trash_collected:
                    self.trash_collected[item_name] = True
                    self._check_key_unlock()
                self._update_score(item_name, location.id_num)
            else:
                print(f"You don't have a {item_name} to drop.")
        else:
            print("Invalid command.")

    def _check_key_unlock(self) -> None:
        """Check whether all trash has been picked up."""
        if all(self.trash_collected.values()):
            dorm = self._locations[0]
            dorm.items.append("locker key")
            print("A locker key falls out of the trash can! You pick it up automatically.")
            self.inventory.append("locker key")

    def _undo_last_action(self) -> None:
        """Undo the last action taken by the player."""
        if not self.event_log.is_empty():
            last_event = self.event_log.last
            if last_event.next_command == "pick up":
                item_name = last_event.description.split(" ")[-1]
                self.inventory.remove(item_name)
                self.get_location(last_event.id_num).items.append(item_name)
            elif last_event.next_command == "drop":
                item_name = last_event.description.split(" ")[-1]
                self.inventory.append(item_name)
                self.get_location(last_event.id_num).items.remove(item_name)
            self.event_log.remove_last_event()
            print("Undid the last action.")
        else:
            print("No actions to undo.")


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "undo", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your marks will be based on how well-organized your code is.

        location = game.get_location()

        # TODO: Add new Event to game log to represent current game location
        #  Note that the <choice> variable should be the command which led to this event
        # YOUR CODE HERE

        # TODO: Depending on whether or not it's been visited before,
        #  print either full description (first time visit) or brief description (every subsequent visit) of location
        # YOUR CODE HERE

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice in menu:
            # TODO: Handle each menu command as appropriate
            # Note: For the "undo" command, remember to manipulate the game_log event list to keep it up-to-date
            if choice == "log":
                game_log.display_events()
            # ENTER YOUR CODE BELOW to handle other menu commands (remember to use helper functions as appropriate)

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result

            # TODO: Add in code to deal with actions which do not change the location (e.g. taking or using an item)
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game
