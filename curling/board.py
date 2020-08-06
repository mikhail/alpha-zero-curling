import logging
from typing import Tuple, Generator

import numpy as np

from curling import constants as c
from curling import utils


# Board shape"
# x values. p1...p1, p2...p2
# y values
# 0,1 - has this stone been thrown yet
# 0,1 - is this stone "valid" (1) or "out of play" (0) (touched a wall)

# [
#     [0] * 16,
#     [0] * 16,
#     [0] * 16,
#     [1] * 16
# ]

def stones_for_team(board: np.array, team: int):
    start = 0
    if team == c.P2:
        start = 8

    for i in range(start, start + 8):
        yield board[:, i]


def get_xy_team1(board: np.array) -> Generator[Tuple[float, float], None, None]:
    """Returns list of x,y coordinates of thrown stones still in play."""
    for i in range(8):
        if board[c.BOARD_THROWN][i] == c.THROWN and board[c.BOARD_IN_PLAY][i] == c.IN_PLAY:
            yield board[c.BOARD_X][i], board[c.BOARD_Y][i]


def get_xy_team2(board: np.array) -> Generator[Tuple[float, float], None, None]:
    """Returns list of x,y coordinates of thrown stones still in play."""
    for i in range(8, 16):
        if board[c.BOARD_THROWN][i] == c.THROWN and board[c.BOARD_IN_PLAY][i] == c.IN_PLAY:
            yield board[c.BOARD_X][i], board[c.BOARD_Y][i]


def removed_stones_team1(board: np.array) -> int:
    return 8 - sum(board[c.BOARD_IN_PLAY][0:8])


def removed_stones_team2(board: np.array) -> int:
    return 8 - sum(board[c.BOARD_IN_PLAY][8:16])


def get_data_rows(board: np.array) -> np.array:
    return board[c.BOARD_Y + 1:]  # everything except x and y rows


def getInitBoard():
    board = np.zeros(getBoardSize(), float)
    # x values. p1...p1, p2...p2
    # y values
    # 0,1 - has this stone been thrown yet
    # 0,1 - is this stone "in play" (1) or "out of play" (0) (touched a wall)
    board[c.BOARD_X] = [0] * 16
    board[c.BOARD_Y] = [0] * 16
    board[c.BOARD_THROWN] = [c.NOT_THROWN] * 16
    board[c.BOARD_IN_PLAY] = [c.IN_PLAY] * 16
    return board


def getBoardSize():
    return 4, 16


def thrownStones(board):
    logging.warning('Try using sim.space.thrownStonesCount() instead.')
    return sum(board[c.BOARD_THROWN])


def scenario_all_out_of_play(board):
    board[c.BOARD_THROWN].fill(c.THROWN)
    board[c.BOARD_IN_PLAY].fill(c.OUT_OF_PLAY)


def set_stone(board, player, stone_id, x, y, thrown=c.THROWN, in_play=c.IN_PLAY):
    assert player in [c.P1, c.P2]
    assert 0 <= stone_id <= 7

    if player == c.P1:
        stone = board[:, stone_id]
    else:
        stone = board[:, stone_id + 8]

    stone[c.BOARD_X] = x
    stone[c.BOARD_Y] = y
    stone[c.BOARD_THROWN] = thrown
    stone[c.BOARD_IN_PLAY] = in_play


def configure_hammer_1_scenario(board):
    scenario_all_out_of_play(board)

    hammer = board[:, -1]
    hammer[c.BOARD_X] = 0
    hammer[c.BOARD_Y] = utils.TEE_LINE
    hammer[c.BOARD_THROWN] = c.THROWN
    hammer[c.BOARD_IN_PLAY] = c.IN_PLAY


def configure_hammer_2_scenario(board):
    configure_hammer_1_scenario(board)

    stone = board[:, -2]
    stone[c.BOARD_X] = 0 + utils.STONE_RADIUS
    stone[c.BOARD_Y] = utils.TEE_LINE + utils.STONE_RADIUS
    stone[c.BOARD_THROWN] = c.THROWN
    stone[c.BOARD_IN_PLAY] = c.IN_PLAY
