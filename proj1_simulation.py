"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate an entire
playthrough of the game. Please consult the project handout for instructions and details.

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
from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough with enhanced item handling."""

    # Private Instance Attributes:
    #   - _game: The AdventureGame instance with full game state tracking
    #   - _events: EventList tracking all game events
    #   - _inventory: Simulated player inventory
    #   - _score: Simulated player score

    _game: AdventureGame
    _events: EventList
    _inventory: list[str]
    _score: int

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation with full state tracking."""
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)
        self._inventory = []
        self._score = 0

        initial_location = self._game.get_location()
        self._events.add_event(Event(initial_location.id_num, initial_location.long_description))
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)
        # Hint: self._game.get_location() gives you back the current location
        self._process_commands(commands)

        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, initial_location)

    def handle_pick_up(self, item: str, current_loc: Location) -> None:
        """Handles picking up an item from the current location."""
        if item in current_loc.items:
            self._inventory.append(item)
            current_loc.items.remove(item)

    def handle_drop(self, item: str, current_loc: Location) -> None:
        """Handles dropping an item at the current location.
        Also updates trash status and inventory if conditions are met."""
        if item in self._inventory:
            self._inventory.remove(item)
            current_loc.items.append(item)

            if current_loc.id_num == 6 and item in self._trash_status:
                self._trash_status[item] = True
                self._score += 1

            if all(self._trash_status.values()) and "locker key" not in self._inventory:
                self._inventory.append("locker key")
                print("Key added to inventory")

    def handle_go(self, direction: str, current_loc: Location) -> Location:
        """Handles moving to a new location if the direction is valid."""
        if direction in current_loc.available_commands:
            next_loc_id = current_loc.available_commands[direction]
            next_loc = self._game.get_location(next_loc_id)

            if next_loc.id_num == 2 and not next_loc.locked:
                if "locker key" in self._inventory:
                    next_loc.locked = False
                    next_loc.items.append("USB drive")  # Add USB drive to locker

            return next_loc
        return current_loc

    def _process_commands(self, commands: list[str]) -> None:
        """Process the commands."""
        current_loc = self._game.get_location()

        for cmd in commands:
            if cmd.startswith("pick up"):
                item = cmd.split("pick up ")[1]
                self.handle_pick_up(item, current_loc)
            elif cmd.startswith("drop"):
                item_name = cmd.split("drop ")[1]
                self.handle_drop(item_name, current_loc)
            elif cmd.startswith("go"):
                direction = cmd.split(" ")[1]
                current_loc = self.handle_go(direction, current_loc)

            self._events.add_event(Event(current_loc.id_num, current_loc.brief_description), cmd)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """Generate all events in this simulation.

            Preconditions:
            - len(commands) > 0
            - all commands in the given list are valid commands at each associated location in the game
            """

        # Hint: current_location.available_commands[command] will return the next location ID
        # which executing <command> while in <current_location_id> leads to
        for command in commands:
            next_location_id = current_location.available_commands[command]
            next_location = self._game.get_location(next_location_id)
            next_event = Event(next_location.id_num, next_location.brief_description)
            self._events.add_event(next_event, command)
            current_location = next_location

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east"])
        >>> sim.get_id_log()
        [1, 2]

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east", "go east", "buy coffee"])
        >>> sim.get_id_log()
        [1, 2, 3, 3]
        """

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and log location descriptions."""

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    win_walkthrough = [
        "pick up waste paper",
        "pick up food scraps",
        "pick up waste bottles",
        "pick up vegetable peelings",
        "go north",
        "drop waste paper",
        "drop food scraps",
        "drop waste bottles",
        "drop vegetable peelings",
        "go west",  # To locker
        "pick up USB drive",
        "go east",
        "go south",  # To dorm
        "drop USB drive"
        "go west"   # To starbucks
        "pick up UofT mug"
        "go east"
        "drop UofT mug"
        "go south",  # To Bahen 1F
        "pick up toonie",
        "go west",  # To the lost and found office
        "drop toonie",
        "go east",  # To Bahen
        "pick up textbook"
        "go south",  # To Robarts
        "drop textbook"
        "go west",  # To reading room
        "pick up laptop charger",
        "go east",  # To Robarts
        "go north",  # To Bahen
        "go north",  # To dorm
        "drop laptop charger"]

    expected_log = [0, 0, 0, 0,
                    6, 6, 6, 6, 6,
                    2, 2, 6,
                    0, 0, 5, 5, 0, 0,
                    1, 1, 4, 4, 1, 3, 3,
                    1, 3, 7, 7,
                    3, 1, 0]
    # Uncomment the line below to test your walkthrough
    sim = AdventureGameSimulation('game_data.json', 0, win_walkthrough)
    assert expected_log == sim.get_id_log()

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    lose_demo = ["go south",
                 "go west",
                 "go east",
                 "quit"]
    expected_log = [0, 1, 4, 0]  # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your demo
    sim = AdventureGameSimulation('game_data.json', 0, win_walkthrough)
    assert expected_log == sim.get_id_log()

    # TODO: Add code below to provide walkthroughs that show off certain features of the game
    # TODO: Create a list of commands involving visiting locations, picking up items, and then
    #   checking the inventory, your list must include the "inventory" command at least once
    # inventory_demo = [..., "inventory", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # scores_demo = [..., "score", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Add more enhancement_demos if you have more enhancements
    # enhancement1_demo = [...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Note: You can add more code below for your own testing purposes



