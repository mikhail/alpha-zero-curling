EMPTY = 0

P1_COLOR = 'red'
P1 = 1
P1_NOT_THROWN = 2
P1_OUT_OF_PLAY = 3

P2_COLOR = 'blue'
P2 = -1
P2_NOT_THROWN = -2
P2_OUT_OF_PLAY = -3

STONE_RADIUS_IN = 5.73
STONE_MASS = 2  # units don't matter... 1 'stone" weight.
G_FORCE = 9.81  # In meters
SURFACE_FRICTION = 0.02  # Experimentally picked -- draw weight of 20s
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
ACTION_LIST = tuple(
    (h, w, b)
    for h in HANDLES
    for w in WEIGHT_FT.keys()
    for b in BROOMS
)
BOARD_RESOLUTION = 0.2  # X pixels per inch. Higher is better but calculations are slower
