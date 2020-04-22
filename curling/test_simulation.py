"""
To run tests:
pytest test_game.py
"""

import numpy as np

from curling import constants as c
from curling import game
from curling import simulation
from curling import utils


def test_simulation_setupBoard_0():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    sim = simulation.Simulation(board)
    sim.setupBoard(board)

    stones = list(sim.getStones())
    assert len(stones) == 0


def test_simulation_setupBoard_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[1][1] = c.P1
    board[2][2] = c.P2

    sim = curl.sim
    sim.setupBoard(board)

    stones = list(sim.getStones())
    assert len(stones) == 2


def test_simulation_setupBoard_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0] = c.P1_OUT_OF_PLAY
    board[-1][8] = c.EMPTY

    curl.sim.setupBoard(board)
    stones = list(curl.sim.getStones())
    assert len(stones) == 0


def test_simulation_getNextStoneId():
    curl = game.CurlingGame()

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 0  # for red

    curl.sim.addStone(c.P1_COLOR, 0, utils.HOG_LINE)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 8  # for blue

    curl.sim.addStone(c.P2_COLOR, 1, utils.HOG_LINE)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 1  # for red

    curl.sim.addStone(c.P1_COLOR, 2, utils.HOG_LINE)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 9  # for blue


def test_simulation_getBoard():
    curl = game.CurlingGame()

    expected = curl.sim.getBoard()
    expected[2][2] = c.P1
    expected[-1][0] = c.EMPTY

    curl.sim.setupBoard(expected)
    actual = curl.sim.getBoard()

    np.testing.assert_array_equal(actual, expected)


def test_simulation_getBoard_button():
    sim = game.CurlingGame().sim

    board = sim.getBoard()
    board[-1][0] = c.EMPTY

    button_x, button_y = game.BUTTON_POSITION
    board_x, board_y = utils.realToBoard(button_x, button_y)

    board[board_x][board_y] = c.P1
    sim.setupBoard(board)

    stones = sim.getStones()
    assert len(stones) == 1

    stone_x, stone_y = stones[0].body.position
    assert (button_x, button_y) == (stone_x, stone_y)
    recalculated_board = sim.getBoard()

    expected = np.argwhere(board == c.P1)
    actual = np.argwhere(recalculated_board == c.P1)
    np.testing.assert_array_equal(expected, actual)


def test_simulation_getBoard_right_edge():
    sim = game.CurlingGame().sim

    board = sim.getBoard()
    board[-1][0] = c.EMPTY

    button_x, button_y = game.BUTTON_POSITION
    button_x -= utils.dist(inches=10)
    board_x, board_y = utils.realToBoard(button_x, button_y)

    board[board_x][board_y] = c.P1
    sim.setupBoard(board)

    stones = sim.getStones()
    assert len(stones) == 1

    stone_x, stone_y = stones[0].body.position
    assert (button_x, button_y) == (stone_x, stone_y)
    recalculated_board = sim.getBoard()

    expected = np.argwhere(board == c.P1)
    actual = np.argwhere(recalculated_board == c.P1)
    np.testing.assert_array_equal(expected, actual)


def test_simulation_getBoard_with_invalid():
    curl = game.CurlingGame()

    expected = curl.sim.getBoard()
    expected[-1][0] = c.P1_OUT_OF_PLAY
    expected[-1][8] = c.P2_OUT_OF_PLAY
    expected[-1][1] = c.P1_OUT_OF_PLAY
    expected[-1][9] = c.P2_OUT_OF_PLAY

    curl.sim.setupBoard(expected)
    actual = curl.sim.getBoard()

    np.testing.assert_array_equal(actual[-1][0:16], expected[-1][0:16])
