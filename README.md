# Battleship

Battleship is a classic two-player guessing game where opponents attempt to locate and sink each other's concealed fleet of ships. The bot takes on the role of the second player.

## Requirements

Python >= 3.10

## Setup

The easiest way to set up the project is to build a Docker image based on the provided Dockerfile and to use it within an interactive bash session. 

```console
$ docker build -t battleship .
$ docker run --rm -it battleship bash
```

## How to Play

Initiate the game by strategically placing the ships on the board. 
Each ship requires the player to input its starting and ending coordinates using 
capital letters and numbers (e.g., "A1 A6"). The ships cannot 
overlap or touch each other.

### Ships Available per Player:

* 1 aircraft (occupying 6 fields)
* 1 aircraft carrier (occupying 4 fields)
* 1 battleship (occupying 4 fields)
* 1 cruiser (occupying 3 fields)
* 2 destroyers (each occupying 2 fields)
* 2 submarines (each occupying 1 field)

During gameplay, the board displays outcomes using symbols:

* ≈ denotes hitting the water.
* ╳ signifies a successful hit on an opponent's ship.

Victory in the game is achieved by successfully sinking all the opponent's ships before 
the opponent accomplishes the same feat. Strategic planning and precise targeting are 
crucial to emerging victorious in this tactical naval battle.
