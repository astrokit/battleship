from collections import deque
from enum import Enum
import json
import random
import re


class Orientation(Enum):
    horizontal = 0
    vertical = 1


class GameData:
    def __init__(self, **entries):
        self.ships_player1 = {
            "aircraft": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "aircraftcarrier": {
                "start": "",
                "end": "",
                "orientation": Orientation.horizontal,
                "dead": False,
                "hits": [],
            },
            "battleship": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "cruiser": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "destroyer1": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "destroyer2": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "submarine1": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "submarine2": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
        }

        self.ships_player2 = {
            "aircraftcarrier": {
                "start": "",
                "end": "",
                "orientation": Orientation.horizontal,
                "dead": False,
                "hits": [],
            },
            "battleship": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "cruiser": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "destroyer1": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "destroyer2": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "submarine1": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
            "submarine2": {"start": "", "end": "", "orientation": Orientation.horizontal, "dead": False, "hits": []},
        }

        # Bot attack strategy
        self.attackinfo_player2 = {
            "mode": 0,
            "coords_to_visit": deque(),
            "coords_to_visit_orientation": {},
            "firsthit_coord": "",
            "orientation": "",
        }

        # Coordinate maps where ship + adjacent coordinates are set to the shipname for easy collsion check
        self.ships_player1_hidden = {}
        self.ships_player2_hidden = {}

        self.__dict__.update(entries)


"""
A Custom JSONEncoder used to encode the GameData class
"""


class GameDataJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GameData):
            return obj.__dict__
        if isinstance(obj, Enum):
            return obj.value
        else:
            return json.JSONEncoder.default(self, obj)


"""
Python dictionaries are unsorted by default, if you have to sort the Keys see def board(coordinates)
"""
coordinates: dict[str, str] = {
    'A1': ' ', 'A2': ' ', 'A3': ' ', 'A4': ' ', 'A5': ' ',
    'A6': ' ', 'A7': ' ', 'A8': ' ', 'A9': ' ', 'A0': ' ',
    'B1': ' ', 'B2': ' ', 'B3': ' ', 'B4': ' ', 'B5': ' ',
    'B6': ' ', 'B7': ' ', 'B8': ' ', 'B9': ' ', 'B0': ' ',
    'C1': ' ', 'C2': ' ', 'C3': ' ', 'C4': ' ', 'C5': ' ',
    'C6': ' ', 'C7': ' ', 'C8': ' ', 'C9': ' ', 'C0': ' ',
    'D1': ' ', 'D2': ' ', 'D3': ' ', 'D4': ' ', 'D5': ' ',
    'D6': ' ', 'D7': ' ', 'D8': ' ', 'D9': ' ', 'D0': ' ',
    'E1': ' ', 'E2': ' ', 'E3': ' ', 'E4': ' ', 'E5': ' ',
    'E6': ' ', 'E7': ' ', 'E8': ' ', 'E9': ' ', 'E0': ' ',
    'F1': ' ', 'F2': ' ', 'F3': ' ', 'F4': ' ', 'F5': ' ',
    'F6': ' ', 'F7': ' ', 'F8': ' ', 'F9': ' ', 'F0': ' ',
    'G1': ' ', 'G2': ' ', 'G3': ' ', 'G4': ' ', 'G5': ' ',
    'G6': ' ', 'G7': ' ', 'G8': ' ', 'G9': ' ', 'G0': ' ',
    'H1': ' ', 'H2': ' ', 'H3': ' ', 'H4': ' ', 'H5': ' ',
    'H6': ' ', 'H7': ' ', 'H8': ' ', 'H9': ' ', 'H0': ' ',
    'I1': ' ', 'I2': ' ', 'I3': ' ', 'I4': ' ', 'I5': ' ',
    'I6': ' ', 'I7': ' ', 'I8': ' ', 'I9': ' ', 'I0': ' ',
    'J1': ' ', 'J2': ' ', 'J3': ' ', 'J4': ' ', 'J5': ' ',
    'J6': ' ', 'J7': ' ', 'J8': ' ', 'J9': ' ', 'J0': ' '
}


"""
 ship: ◯ (U+25EF)
 hit: ╳  (U+2573)
 miss: ≈ (U+2248)
"""


def board(coordinates):
    printboard = "   ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐\n"

    last_key = "A"
    line = " "
    line = line + last_key
    line = line + " │"
    keylist = list(coordinates.keys())

    for key in sorted(keylist):
        if key[0] == last_key:
            line = line + " " + coordinates[key] + " " + "│"
        else:
            printboard += line
            printboard += "\n   ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤\n"
            line = " "
            last_key = key[0]
            line = line + last_key
            line = line + " │"
            line = line + " " + coordinates[key] + " " + "│"
    printboard += line
    printboard += "\n   └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘"
    printboard += "\n     0   1   2   3   4   5   6   7   8   9   "

    return printboard


def get_all_ship_coordinates(coord_start, coord_end, orientation):
    ship_coordinates = []

    if orientation == Orientation.horizontal:
        # Go through each field in x-direction, e.g., A0 A4 -> A0 A1 A2 A3 A4
        for x in range(int(coord_start[1]), int(coord_end[1]) + 1):
            coord = coord_start[0] + str(x)
            ship_coordinates.append(coord)
    else:
        # Go through each field in y-direction, e.g., B8 F8 -> B8 C8 D8 E8 F8
        for y in range(ord(coord_start[0]), ord(coord_end[0]) + 1):
            coord = chr(y) + coord_start[1]
            ship_coordinates.append(coord)

    return ship_coordinates


def get_surrounding_coordinates(coord):
    coords = []

    if int(coord[1]) - 1 >= 0:
        coords.append(coord[0] + str(int(coord[1]) - 1))  # left
        if ord(coord[0]) - 1 >= ord("A"):
            coords.append(chr(ord(coord[0]) - 1) + str(int(coord[1]) - 1))  # left-up
        if ord(coord[0]) + 1 <= ord("J"):
            coords.append(chr(ord(coord[0]) + 1) + str(int(coord[1]) - 1))  # left-below
    if int(coord[1]) + 1 <= 9:
        coords.append(coord[0] + str(int(coord[1]) + 1))  # right
        if ord(coord[0]) - 1 >= ord("A"):
            coords.append(chr(ord(coord[0]) - 1) + str(int(coord[1]) + 1))  # right-up
        if ord(coord[0]) + 1 <= ord("J"):
            coords.append(chr(ord(coord[0]) + 1) + str(int(coord[1]) + 1))  # right-below
    if ord(coord[0]) - 1 >= ord("A"):
        coords.append(chr(ord(coord[0]) - 1) + coord[1])  # up
    if ord(coord[0]) + 1 <= ord("J"):
        coords.append(chr(ord(coord[0]) + 1) + coord[1])  # below

    return coords


def read_player_coordinates(gd, shipname, shipsize):
    str_coordinates = "coordinates"
    str_coordinates_expected = "2"
    str_fields = "fields"
    regex_coordnumber = r"^([A-Z]\d+)\s([A-Z]\d+)$"
    regex_coordinfield = r"^([A-J][0-9])\s([A-J][0-9])$"

    if shipsize == 1:
        str_coordinates = "coordinate"
        str_coordinates_expected = "1"
        str_fields = "field"
        regex_coordnumber = r"^([A-Z]\d+)$"
        regex_coordinfield = r"^([A-J][0-9])$"

    # Read player input, e.g., set coordinates for aircraftcarrier (5 fields): A2 A6
    playerinput = input("set {} for {} ({} {}): ".format(str_coordinates, shipname, shipsize, str_fields))

    # Ensure amount of provided coordinates is 1 or 2 (depending on shipsize)
    m = re.match(regex_coordnumber, playerinput)
    if m:
        # Ensure given coordinates are within the field and in the format [A-J][0-9]
        m = re.match(regex_coordinfield, playerinput)
        if m:
            # Ensure the size of the ship matches the coordinates, e.g., A0 A4 => 5
            if shipsize != 1:
                coord1 = m.group(1)  # [A-J][0-9]
                coord2 = m.group(2)  # [A-J][0-9]
                shipsize1 = shipsize - 1  # because, e.g., A1 A5 are 5 fields but 5-1 = 4 and not 5

                if coord1[0] == coord2[0] and (ord(coord2[1]) - ord(coord1[1])) == shipsize1:
                    # e.g., coord1 = A1, coord2 = A5 --> if (A == A and 5-1 == 4):
                    orientation = Orientation.horizontal
                elif coord1[1] == coord2[1] and (ord(coord2[0]) - ord(coord1[0])) == shipsize1:
                    # e.g., coord1 = B8, coord2 = F8 --> if (8 == 8 and F-B == 4):
                    orientation = Orientation.vertical
                else:
                    print("Your end coordinate is invalid.")
                    return read_player_coordinates(gd, shipname, shipsize)
            else:  # submarine (1 field)
                coord1 = coord2 = m.group(1)
                orientation = Orientation.horizontal

            # Check if ship would overlap or adjoin
            collidingship = None
            all_ship_coordinates = get_all_ship_coordinates(coord1, coord2, orientation)
            for ship_coord in all_ship_coordinates:
                if ship_coord in gd.ships_player1_hidden:
                    collidingship = gd.ships_player1_hidden[ship_coord]
                    break

            if collidingship is None:
                # Store ship coordinates
                gd.ships_player1[shipname]["start"] = coord1
                gd.ships_player1[shipname]["end"] = coord2
                gd.ships_player1[shipname]["orientation"] = orientation

                # Draw all ship coordinates in map
                for ship_coord in all_ship_coordinates:
                    gd.coordinates_player1[ship_coord] = "\u25EF"

                    # Internally assign the ship name to all ship coordinates and surrounding coordinates.
                    # This enables a simple collision check because we just have to go through the dict.
                    gd.ships_player1_hidden[ship_coord] = shipname
                    ship_surrounding_coords = get_surrounding_coordinates(ship_coord)
                    for ship_surrounding_coord in ship_surrounding_coords:
                        gd.ships_player1_hidden[ship_surrounding_coord] = shipname

                print(board(gd.coordinates_player1))
            else:
                print("Ship overlaps or adjoins {}. Reposition {}.".format(collidingship, shipname))
                return read_player_coordinates(gd, shipname, shipsize)
        else:
            print("You entered an invalid coordinate.")
            return read_player_coordinates(gd, shipname, shipsize)
    else:
        print("Please specify {} {}.".format(str_coordinates_expected, str_coordinates))
        return read_player_coordinates(gd, shipname, shipsize)


def player_shoot(gd):
    # Read player input, e.g., Enter target coordinate: A0
    playerinput = input("Enter target coordinate: ")

    # Ensure given coordinates are within the field and in the format [A-J][0-9]
    m = re.match(r"^([A-J]\d)$", playerinput)
    if m:
        coord = m.group(1)  # [A-J][0-9]
        # Ensure the player has not tried this coordinate previously (if so, there would be hit or miss symbol on coord)
        if gd.coordinates_player1_guesses[coord] == " ":
            # If there is something at this coordinate, we have a hit
            if gd.coordinates_player2[coord] != " ":
                gd.coordinates_player1_guesses[coord] = "\u2573"

                # Store the hit with the corresponding ship
                shipname = gd.ships_player2_hidden[coord]
                gd.ships_player2[shipname]["hits"].append(coord)

                # Check if we only hit a ship part or sank the entire ship
                all_ship_coordinates = get_all_ship_coordinates(
                    gd.ships_player2[shipname]["start"],
                    gd.ships_player2[shipname]["end"],
                    gd.ships_player2[shipname]["orientation"],
                )
                if len(gd.ships_player2[shipname]["hits"]) == len(all_ship_coordinates):
                    gd.ships_player2[shipname]["dead"] = True
                    print("You sank {}.".format(shipname))
                else:
                    print("You hit a ship.")
            else:
                gd.coordinates_player1_guesses[coord] = "\u2248"
                print("You only hit the water.")
        else:
            print("Coordinate has already been selected. Please select another coordinate.")
            return player_shoot(gd)
    else:
        print("You entered an invalid coordinate.")
        return player_shoot(gd)


def bot_place_ship(gd, shipname, shipsize):
    # Randomly choose if the ship should be aligned horizontally or vertically
    orientation = random.randint(0, 1)
    if orientation == 0:
        orientation = Orientation.horizontal

        # Ship position on the y-axis. Will be the same for start and end as the orientation is horizontal, e.g., A0 A4
        y12 = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])
        # Ship start point on the x-axis. We take 9-shipsize because otherwise the ship would not fit anyway
        # +1 because e.g., A5 A9 are 5 fields but 9-5 = 4 and not 5
        x1 = random.randint(0, 9 - shipsize + 1)
        # Ship end point on the x-axis
        x2 = x1 + shipsize - 1  # -1 because e.g., A5 + 5 fields would end on A10 and not on A9

        coord1 = y12 + str(x1)
        coord2 = y12 + str(x2)
    else:
        orientation = Orientation.vertical

        # Ship position on the x-axis will be the same for both points as the orientation is vertical, e.g., F8 J8
        x12 = random.randint(0, 9)
        # Ship start point on the y-axis. We reduce the list by points that would be too small for the ship to fit
        y_choices = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        if shipsize != 1:  # needed because with shipsize == 1, y_choices would be [:0] -> empty list
            y_choices = y_choices[: -shipsize + 1]
        y1 = random.choice(y_choices)
        # Ship end point on the y-axis
        y2 = chr(ord(y1) + shipsize - 1)  # -1 because e.g., F8 + 5 fields would end on K8 and not on J8

        coord1 = y1 + str(x12)
        coord2 = y2 + str(x12)

    # Check if ship would overlap or adjoin
    collidingship = None
    all_ship_coordinates = get_all_ship_coordinates(coord1, coord2, orientation)
    for ship_coord in all_ship_coordinates:
        if ship_coord in gd.ships_player2_hidden:
            collidingship = gd.ships_player2_hidden[ship_coord]
            break

    if collidingship is None:
        # Store ship coordinates
        gd.ships_player2[shipname]["start"] = coord1
        gd.ships_player2[shipname]["end"] = coord2
        gd.ships_player2[shipname]["orientation"] = orientation

        # Draw all ship coordinates in map
        for ship_coord in all_ship_coordinates:
            gd.coordinates_player2[ship_coord] = "\u25EF"

            # Internally assign the ship name to all ship coordinates and surrounding coordinates.
            # This enables a simple collision check because we just have to go through the dict.
            gd.ships_player2_hidden[ship_coord] = shipname
            ship_surrounding_coords = get_surrounding_coordinates(ship_coord)
            for ship_surrounding_coord in ship_surrounding_coords:
                gd.ships_player2_hidden[ship_surrounding_coord] = shipname
    else:
        # Bot chosen coordinate causes a collision -> re-try the ship placement
        return bot_place_ship(gd, shipname, shipsize)


def bot_get_possible_ship_coordinates(gd, coord, direction):
    todofields = []

    fields_to_go_switcher = {
        "left": int(coord[1]),
        "right": 9 - int(coord[1]),
        "up": ord(coord[0]) - ord("A"),
        "below": ord("J") - ord(coord[0]),
    }
    fields_to_go = fields_to_go_switcher.get(direction, 0)

    # If fields_to_go == 0 we have reached a border 0 (left), 9 (right), A (up), J (below) -> no sense to proceed then
    if fields_to_go > 0:
        fields_to_go = min(fields_to_go, 4)  # max. ship lentgh is 5, so do not try to visit more than nearby 4 fields
        while fields_to_go > 0:
            coord_switcher = {
                "left": coord[0] + str(int(coord[1]) - 1),
                "right": coord[0] + str(int(coord[1]) + 1),
                "up": chr(ord(coord[0]) - 1) + coord[1],
                "below": chr(ord(coord[0]) + 1) + coord[1],
            }
            # Select an adjacent coordinate depending on the given direction
            coord = coord_switcher.get(direction)

            if gd.coordinates_player1[coord] == "\u2248":  # miss
                # If we already visited this coord earlier and had a miss, going further would make no sense
                break
            else:
                todofields.append(coord)

            fields_to_go -= 1

    return todofields


def bot_evaluate_shooting(gd, coord, status):
    """
    bot_evaluate_shooting is always called after a bot's strike and depending on the status will adapt the strategy.
    coord is the last tried coordinate, status is the strike result: hit, miss, or sank

    It performs the following steps (attack modes): seek (0), explore (1), sink (2)
    """

    if gd.attackinfo_player2["mode"] == 0:  # seek
        # If status == 'miss': Do nothing, try again randomly next time.
        # If status == 'sank': Sinking was successful on the first try (submarine, 1 field only). Try again randomly.

        if status == "hit":
            # We have a hit at coordinate coord -> generate a list of coordinates to try clockwise

            # Generate dict with clockwise adjacent coordinates: up, right, below, left
            # We also immediately store their orientation with respect to the hit coordinate to avoid a later comparison
            coords_to_visit_orientation = {}

            if ord(coord[0]) - 1 >= ord("A"):
                coords_to_visit_orientation[chr(ord(coord[0]) - 1) + coord[1]] = Orientation.vertical  # up
            if int(coord[1]) + 1 <= 9:
                coords_to_visit_orientation[coord[0] + str(int(coord[1]) + 1)] = Orientation.horizontal  # right
            if ord(coord[0]) + 1 <= ord("J"):
                coords_to_visit_orientation[chr(ord(coord[0]) + 1) + coord[1]] = Orientation.vertical  # below
            if int(coord[1]) - 1 >= 0:
                coords_to_visit_orientation[coord[0] + str(int(coord[1]) - 1)] = Orientation.horizontal  # left

            # Remember where we have this first hit
            gd.attackinfo_player2["firsthit_coord"] = coord

            # coords_to_visit is the to do list (deque) of coordinates the bot will check next
            gd.attackinfo_player2["coords_to_visit"] = deque(list(coords_to_visit_orientation))
            # coords_to_visit_orientation is to keep an internal reference about the orientation of the coordinates
            gd.attackinfo_player2["coords_to_visit_orientation"] = coords_to_visit_orientation

            # Switch to next attack mode - explore the surrounding (up, right, below, left)
            gd.attackinfo_player2["mode"] = 1

    elif gd.attackinfo_player2["mode"] == 1:  # explore -> get orientation via todolist
        # If status == 'miss': Clockwise coord from todolist was not successful. Probably the next one will be.

        if status == "hit":
            # We have found a neighboring coordinate -> get the orientation
            gd.attackinfo_player2["orientation"] = gd.attackinfo_player2["coords_to_visit_orientation"][coord]

            if gd.attackinfo_player2["orientation"] == Orientation.horizontal:
                # Rewrite the todolist with coordinates from the left
                coords_to_visit = bot_get_possible_ship_coordinates(gd, gd.attackinfo_player2["firsthit_coord"], "left")
                if not coords_to_visit:
                    # If there are no more coordinates left, e.g., coord == A0, B0, C0 -> immediately go right instead
                    coords_to_visit = bot_get_possible_ship_coordinates(
                        gd, gd.attackinfo_player2["firsthit_coord"], "right"
                    )
            else:
                # Rewrite the todolist with coordinates from upwards
                coords_to_visit = bot_get_possible_ship_coordinates(gd, gd.attackinfo_player2["firsthit_coord"], "up")
                if not coords_to_visit:
                    # If there are no more coordinates up, e.g., coord == A1, A2, A3 -> immediately go down instead
                    coords_to_visit = bot_get_possible_ship_coordinates(
                        gd, gd.attackinfo_player2["firsthit_coord"], "below"
                    )

            # Store the todolist for the next run
            gd.attackinfo_player2["coords_to_visit"] = deque(coords_to_visit)

            # Switch to next attack mode - kill the ship
            gd.attackinfo_player2["mode"] = 2

        elif status == "sank":
            # A coord from the todolist led to a sink -> We are done. Try again randomly next time. New mode: seek (0)
            gd.attackinfo_player2["mode"] = 0

    elif gd.attackinfo_player2["mode"] == 2:  # sink -> try to bring down the ship going to the right or downwards
        # If status == 'hit': Do nothing because there might be more still hits on the left or right

        # Two possibilities:
        # 1) We have a miss in direction X, then try to go the other direction
        # 2) We have a hit in direction X but no more coordinates to try in this direction, so go the other way
        if status == "miss" or (status == "hit" and not gd.attackinfo_player2["coords_to_visit"]):
            if gd.attackinfo_player2["orientation"] == Orientation.horizontal:
                # Rewrite the todolist with coordinates from the right
                gd.attackinfo_player2["coords_to_visit"] = deque(
                    bot_get_possible_ship_coordinates(gd, gd.attackinfo_player2["firsthit_coord"], "right")
                )
            else:
                # Rewrite the todolist with coordinates from below
                gd.attackinfo_player2["coords_to_visit"] = deque(
                    bot_get_possible_ship_coordinates(gd, gd.attackinfo_player2["firsthit_coord"], "below")
                )

        elif status == "sank":
            # A coord from the todolist led to a sink -> We are done. Try again randomly next time. New mode: seek (0)
            gd.attackinfo_player2["mode"] = 0


def bot_get_shooting_coordinate(gd):
    if gd.attackinfo_player2["mode"] == 0:  # seek
        # In seek mode, just pick a random coordinate to try
        y = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])
        x = random.randint(0, 9)
        coord = y + str(x)

        return coord
    elif gd.attackinfo_player2["mode"] > 0:  # explore / sink
        # In explore / sink mode work off the queue
        return gd.attackinfo_player2["coords_to_visit"].popleft()


def bot_shoot(gd):
    coord = bot_get_shooting_coordinate(gd)

    # Ensure the bot has not yet tried hitting this coordinate -> then there would a hit or miss symbol in the field
    if gd.coordinates_player1[coord] not in ["\u2573", "\u2248"]:
        # If there is something at this coordinate, we have a hit
        if gd.coordinates_player1[coord] != " ":
            gd.coordinates_player1[coord] = "\u2573"

            # Store the hit with the corresponding ship
            shipname = gd.ships_player1_hidden[coord]
            gd.ships_player1[shipname]["hits"].append(coord)

            # Check if we only hit a ship part or sank the entire ship
            all_ship_coordinates = get_all_ship_coordinates(
                gd.ships_player1[shipname]["start"],
                gd.ships_player1[shipname]["end"],
                gd.ships_player1[shipname]["orientation"],
            )

            if len(gd.ships_player1[shipname]["hits"]) == len(all_ship_coordinates):
                gd.ships_player1[shipname]["dead"] = True
                print("Bot sank {} ({}).".format(shipname, coord))
                bot_evaluate_shooting(gd, coord, "sank")
            else:
                print("Bot hit a ship ({}).".format(coord))
                bot_evaluate_shooting(gd, coord, "hit")
        else:
            gd.coordinates_player1[coord] = "\u2248"
            print("Bot only hit the water ({}).".format(coord))
            bot_evaluate_shooting(gd, coord, "miss")
    else:
        # Bot has already tried this coordinate -> re-try another hit
        return bot_shoot(gd)


def check_game_result(gd):
    total_ship_count = len(gd.ships_player1.items())
    player1_dead_ships_count = len({k: v for k, v in gd.ships_player1.items() if v["dead"]})
    player2_dead_ships_count = len({k: v for k, v in gd.ships_player2.items() if v["dead"]})

    if player1_dead_ships_count == total_ship_count and player2_dead_ships_count == total_ship_count:
        print("The match ended in a draw.")
        return True
    elif player1_dead_ships_count == total_ship_count:
        print("Your opponent won the match.")
        return True
    elif player2_dead_ships_count == total_ship_count:
        print("Congratulations! You won the match.")
        return True

    return False


def start_game():
    game_running = True
    while game_running:
        print(board(coordinates))
        print("Please place your ships...")

        # coordinates_player1: the player's grid
        # coordinates_player2: the bot's grid (should not be shown to the player)
        # coordinates_player1_guesses: the bot's grid with the player's hits / misses
        gd = GameData(
            coordinates_player1=coordinates.copy(),
            coordinates_player2=coordinates.copy(),
            coordinates_player1_guesses=coordinates.copy(),
        )

        read_player_coordinates(gd, "aircraft", 6)
        read_player_coordinates(gd, "aircraftcarrier", 5)
        read_player_coordinates(gd, "battleship", 4)
        read_player_coordinates(gd, "cruiser", 3)
        read_player_coordinates(gd, "destroyer1", 2)
        read_player_coordinates(gd, "destroyer2", 2)
        read_player_coordinates(gd, "submarine1", 1)
        read_player_coordinates(gd, "submarine2", 1)

        print("Bot opponent is placing ships...")
        bot_place_ship(gd, "aircraftcarrier", 5)
        bot_place_ship(gd, "battleship", 4)
        bot_place_ship(gd, "cruiser", 3)
        bot_place_ship(gd, "destroyer1", 2)
        bot_place_ship(gd, "destroyer2", 2)
        bot_place_ship(gd, "submarine1", 1)
        bot_place_ship(gd, "submarine2", 1)

        print("Match starts...")
        print(board(gd.coordinates_player1))
        print(board(gd.coordinates_player1_guesses))

        end = False
        while end is False:
            player_shoot(gd)
            bot_shoot(gd)
            print(board(gd.coordinates_player1))
            print(board(gd.coordinates_player1_guesses))
            end = check_game_result(gd)

        # Ask for rematch
        has_user_decided = False
        while not has_user_decided:
            playerinput = input("Do you want to play a rematch? [y/n] ")
            if playerinput == "y":
                has_user_decided = True
            elif playerinput == "n":
                has_user_decided = True
                game_running = False


def main():
    try:
        start_game()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
