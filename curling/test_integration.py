import logging

import numpy as np

import log_handler
from curling import constants as c
from curling import game
from curling import utils

log = logging.getLogger(__name__)


def test_guard():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))

    p1_stones = len(np.argwhere(next_board == c.P1))

    assert p1_stones == 1
    assert next_player == c.P2

    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert shooter.is_guard


def test_draw():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '7', 6)))

    p1_stones = len(np.argwhere(next_board == c.P1))

    assert p1_stones == 1
    assert next_player == c.P2

    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert not shooter.is_guard


def test_control():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, 'control', 6)))

    p1_stones = len(np.argwhere(next_board == c.P1))

    assert p1_stones == 0
    assert next_player == c.P2


def test_5_rock_rule():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    # Set up a guard
    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 6)))
    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert shooter.is_guard

    # Take it out
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, 'control', 4)))
    assert next_player == c.P1
    assert next_board[-1][8] == c.P2_OUT_OF_PLAY

    p1_stones = len(np.argwhere(next_board == c.P1))
    assert p1_stones == 1, "Player 1 should keep their stone."

    p2_stones = len(np.argwhere(next_board == c.P2))
    assert p2_stones == 0, "Player 2 should have had their stone removed."

    first_stone = curl.sim.getStones()[0]
    assert first_stone.is_guard


def test_5_rock_rule_reverse():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    # Set up a guard
    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((-1, '3', -6)))
    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert shooter.is_guard

    # Take it out
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((-1, 'control', -4)))
    assert next_player == c.P1

    p1_stones = len(np.argwhere(next_board == c.P1))
    assert p1_stones == 1, "Player 1 should keep their stone."

    p2_stones = len(np.argwhere(next_board == c.P2))
    assert p2_stones == 0, "Player 2 should have had their stone removed."

    first_stone = curl.sim.getStones()[0]
    assert first_stone.is_guard


@log_handler.on_error()
def test_occupying_16th_position():
    """
    This test has a case where a stone ends up being very near a wall but not eliminated.
    This revelaed that realToBoard() conversion needed to be shifted down by "1" before returning.
    """
    c.BOARD_RESOLUTION = 0.1
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[14, 20] = 1
    board[10, 20] = 2
    board[-1][0:16] = [3, 3, 3, 3, 3, 0, 2, 2, -3, -3, -3, -3, -3, 0, -2, -2]

    curl.getNextState(board, 1, 162)


@log_handler.on_error()
def test_stone_lands_on_data_row():
    curl = game.CurlingGame()
    boardString = "1:[]:2:[[15, 16]]:d:[3, 3, 3, 3, 3, 3, 3, 2, -3, -3, -3, -3, -3, -3, -3, 0]"
    board = curl.boardFromString(boardString)

    curl.getNextState(board, 1, 54)


def test_infinite_run():
    """
    The spin of these two rocks caused infinite curl because body.angular_velocity was not subject to friction.
    """

    bs = "1:[]:2:[[13, 36]]:d:[3, 0, 0, 0, 2, 2, 2, 2, -3, -3, 0, 0, -2, -2, -2, -2]"
    curl = game.CurlingGame()
    board = curl.boardFromString(bs)

    curl.getNextState(board, 1, 50)


def test_infinite_run_2():
    bs = "1:[[18, 38]]:2:[]:d:[3, 3, 3, 3, 3, 0, 0, 2, -3, -3, -3, -3, -3, -3, 0, -2]"
    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 33)  # 33=(1, '5', 1))"


def test_infinite_run_3():
    bs = "1:[]:2:[[10, 39]]:d:[3, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 69)  # 69=(1, '8', -2))


def test_infinite_run_4():
    bs = "1:[[30, 44]]:2:[]:d:[0, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 123)  # 123=(-1, '5', 0)


def test_infinite_run_5():
    bs = "1:[[0, 46], [1, 40]]:2:[[3, 46], [5, 35]]:d:[3, 0, 0, 2, 2, 2, 2, 2, -3, -3, 0, 0, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 33)  # (1, '5', 1)


def test_infinite_run_6():
    bs = "1:[[16, 41]]:2:[[15, 36]]:d:[3, 0, 2, 2, 2, 2, 2, 2, -3, 0, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 143)  # (-1, '7', -6)


def test_infinite_run_7():
    bs = "1:[]:2:[[12, 34]]:d:[2, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 60)  # (1, '7', 2)


def test_infinite_run_8():
    bs = "1:[]:2:[[8, 43]]:d:[2, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 117)  # (-1, '5', -6)


def test_infinite_run_9():
    bs = "1:[[11, 49]]:2:[[0, 43], [24, 43]]:d:[0, 2, 2, 2, 2, 2, 2, 2, 0, 0, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 124)  # (-1, '5', 1)


def test_infinite_run_10():
    bs = "1:[[5, 53]]:2:[[20, 39]]:d:[0, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 48)  # (1, '6', 3)


def test_infinite_run_11():
    bs = "1:[]:2:[[32, 45]]:d:[2, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 141)  # (-1, '6', 5)


def test_infinite_run_12():
    bs = "1:[[26, 55]]:2:[[27, 50]]:d:[0, 2, 2, 2, 2, 2, 2, 2, 0, -2, -2, -2, -2, -2, -2, -2]"

    curl = game.CurlingGame()
    board = curl.boardFromString(bs)
    curl.getNextState(board, 1, 165)  # (-1, '8', 3)


def test_it_curls_left():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    curl.getNextState(board, 1, utils.getAction(1, '5', 1))

    stone = curl.sim.getStones()[0]

    left_house = game.utils.dist(feet=-5)
    assert stone.body.position.x < left_house  # positive handle, positive broom, should cross over the center


def test_it_curls_right():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    curl.getNextState(board, 1, utils.getAction(-1, '5', -1))

    stone = curl.sim.getStones()[0]

    right_house = utils.dist(feet=5)
    assert stone.body.position.x > right_house  # positive handle, positive broom, should cross over the center
