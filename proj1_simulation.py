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
    """A simulation of an adventure game playthrough.
    """
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # Hint: self._game.get_location() gives you back the current location
        initial_location = self._game.get_location()
        initial_event = Event(initial_location.id_num, initial_location.brief_description)
        self._events.add_event(initial_event)

        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, initial_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """Generate all events in this simulation.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        last_location_id = current_location.id_num
        self._events.add_event(Event(last_location_id, ""))

        for command in commands:
            if command in current_location.available_commands:
                if command.startswith("go "):
                    direction = command.split("go ")[1]
                    self._game.go(direction)
                    new_location = self._game.get_location()

                    if new_location.id_num != last_location_id:
                        self._events.add_event(Event(new_location.id_num, command))
                        current_location = new_location
                        last_location_id = new_location.id_num
                else:
                    if current_location.id_num != last_location_id:
                        self._events.add_event(Event(current_location.id_num, command))
                        last_location_id = current_location.id_num

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
    win_walkthrough = [
        "look", "pick up waste paper", "pick up food scraps", "pick up waste bottles",
        "pick up vegetable peelings", "go north", "look", "drop waste paper",
        "drop food scraps", "drop waste bottles", "drop vegetable peelings",
        "go west", "look", "pick up USB Drive", "go east", "go south",
        "drop USB Drive", "go west", "look", "pick up UofT mug", "go east",
        "drop UofT mug", "go south", "look", "pick up toonie", "go west",
        "look", "drop toonie", "go east", "pick up textbook", "go south",
        "look", "drop textbook", "go west", "look", "pick up laptop charger",
        "go east", "go north", "go north", "drop laptop charger"
    ]

    expected_log = [0, 0, 6, 2, 6, 0, 5, 0, 1, 4, 1, 3, 1, 0]
    sim = AdventureGameSimulation('game_data.json', 0, win_walkthrough)
    assert expected_log == sim.get_id_log()

    lose_demo = ["go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north", "go south", "go north", "go south", "go north", "go south",
                 "go north", "go south", "go north"]
    expected_log = [0, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6,
                    0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6]
    sim = AdventureGameSimulation('game_data.json', 0, lose_demo)
    assert expected_log == sim.get_id_log()

    inventory_demo = ["pick up waste paper", "inventory", "go north", "drop waste paper", "inventory"]
    expected_log = [0, 0, 6]
    sim = AdventureGameSimulation('game_data.json', 0, inventory_demo)
    assert expected_log == sim.get_id_log()

    scores_demo = ["score", "go south", "pick up toonie", "go west", "drop toonie", "score"]
    expected_log = [0, 0, 1, 4]
    sim = AdventureGameSimulation('game_data.json', 0, scores_demo)
    assert expected_log == sim.get_id_log()
