from typing import Tuple, Generator

import numpy as np
import pymunk

from curling import constants as c
from curling import utils

# Board shape"
# x values. p1...p1, p2...p2
# y values
# 0,1 - has this stone been thrown yet
# 0,1 - is this stone "valid" (1) or "out of play" (0) (touched a wall)
# distance to pin
# 0,1 - is scoring

# [
#     [0] * 16,
#     [0] * 16,
#     [0] * 16,
#     [1] * 16
#     [0] * 16,
#     [0] * 16,
# ]

_HOUSE_RAIDUS = utils.dist(feet=6, inches=c.STONE_RADIUS_IN)


def update_distance_and_score(board: np.array):
    for stone in board.T:
        xy = pymunk.Vec2d(stone[c.BOARD_X], stone[c.BOARD_Y])
        stone[c.BOARD_DISTANCE] = utils.euclid(xy, c.BUTTON_POSITION)

    shot_stones = np.argsort(board[c.BOARD_DISTANCE])

    if shot_stones[0] < 8:
        team_range = range(0, 8)
    else:
        team_range = range(8, 16)

    board[c.BOARD_SCORING].fill(c.NOT_SCORING)
    for i in range(8):
        stone_id = shot_stones[i]
        if stone_id not in team_range:
            break
        stone = board[:, stone_id]
        if stone[c.BOARD_THROWN] and stone[c.BOARD_IN_PLAY]:
            stone[c.BOARD_SCORING] = c.SCORING


def get_stones_in_play(board: np.array):
    for stone in board.T:
        if stone[c.BOARD_IN_PLAY] == c.IN_PLAY and stone[c.BOARD_THROWN] == c.THROWN:
            yield stone


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


def get_data_rows(board: np.array) -> np.array:
    return board[c.BOARD_Y + 1:]  # everything except x and y rows


def getInitBoard():
    board = np.zeros(getBoardSize(), float)
    # x values. p1...p1, p2...p2
    # y values
    # 0,1 - has this stone been thrown yet
    # 0,1 - is this stone "in play" (1) or "out of play" (0) (touched a wall)
    board[c.BOARD_X].fill(0)
    board[c.BOARD_Y].fill(0)
    board[c.BOARD_THROWN].fill(c.NOT_THROWN)
    board[c.BOARD_IN_PLAY].fill(c.IN_PLAY)
    board[c.BOARD_DISTANCE].fill(0)
    board[c.BOARD_SCORING].fill(c.NOT_SCORING)
    return board


def getBoardSize():
    return 6, 16


def getBoardRepr(board):
    ret = "\n"
    ret += str(list(map(int, board[0]))) + "\n"
    ret += str(list(map(int, board[1]))) + "\n"
    ret += str(list(map(int, board[2]))) + "\n"
    ret += str(list(map(int, board[3]))) + "\n"
    ret += str(list(map(int, board[4]))) + "\n"
    ret += str(list(map(int, board[5])))
    return ret


def thrownStones(board):
    return np.sum(board[c.BOARD_THROWN])


def thrownStones_team1(board):
    return np.sum(board[c.BOARD_THROWN][0:8])


def thrownStones_team2(board):
    return np.sum(board[c.BOARD_THROWN][8:16])


def scenario_all_out_of_play(board):
    board[c.BOARD_THROWN].fill(c.THROWN)
    board[c.BOARD_IN_PLAY].fill(c.OUT_OF_PLAY)
    board[c.BOARD_DISTANCE].fill(0)
    board[c.BOARD_SCORING].fill(c.NOT_SCORING)


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

    update_distance_and_score(board)


def configure_hammer_1_scenario(board):
    scenario_all_out_of_play(board)

    # TODO: convert to use set_stone()
    hammer = board[:, -1]
    hammer[c.BOARD_X] = 0
    hammer[c.BOARD_Y] = utils.TEE_LINE
    hammer[c.BOARD_THROWN] = c.THROWN
    hammer[c.BOARD_IN_PLAY] = c.IN_PLAY

    update_distance_and_score(board)


def configure_hammer_2_scenario(board):
    # TODO: convert to use set_stone()
    configure_hammer_1_scenario(board)

    stone = board[:, -2]
    stone[c.BOARD_X] = 0 + utils.STONE_RADIUS
    stone[c.BOARD_Y] = utils.TEE_LINE + utils.STONE_RADIUS
    stone[c.BOARD_THROWN] = c.THROWN
    stone[c.BOARD_IN_PLAY] = c.IN_PLAY

    update_distance_and_score(board)
