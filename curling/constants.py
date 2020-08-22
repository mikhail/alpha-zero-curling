from typing import Tuple

import yaml

with open('shared_constants.yaml') as sc_file:
    sc = yaml.load(sc_file)

    STONE_RADIUS_IN = sc['STONE_RADIUS_IN']
    STONE_MASS = sc['STONE_MASS']
    G_FORCE = sc['G_FORCE']
    SURFACE_FRICTION = sc['SURFACE_FRICTION']

EMPTY = 0

NOT_THROWN = 0
THROWN = 1

OUT_OF_PLAY = 0
IN_PLAY = 1

P1_COLOR = 'red'
P1 = 1
P1_NOT_THROWN = 2
P1_OUT_OF_PLAY = 3

P2_COLOR = 'blue'
P2 = -1
P2_NOT_THROWN = -2
P2_OUT_OF_PLAY = -3

# What info is stored in board data
BOARD_X = 0
BOARD_Y = 1
BOARD_THROWN = 2
BOARD_IN_PLAY = 3

DT = 0.016  # Simulation deltaTime
WEIGHT_FT = {
    #    '1': 108,
    #    '2': 112,
    '3': 118,
    '4': 120,
    '5': 122,
    '6': 123,
    '7': 124.5,
    '8': 126,
    #    '9': 127,
    #    '10': 129,
    #    'backline': 130,
    #    'hack': 136,
    #    'board': 142,
    'control': 148,
    #    'normal': 154,
    #    'peel': 160
}
HANDLES = (1, -1)  # rotation velocity
BROOMS = range(-6, 7)
ACTION_LIST: Tuple[Tuple[int, str, int]] = tuple(
    (h, w, b)
    for h in HANDLES
    for w in WEIGHT_FT.keys()
    for b in BROOMS
)
SHORT_ACTION_LIST = [
    (-1, '3', -6),  # Draw
    (-1, '3', 6),  # Hit wall
    (1, '7', 6),  # button
    (1, 'control', -6)  # through
]
