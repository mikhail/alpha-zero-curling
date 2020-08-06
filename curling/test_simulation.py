"""
To run tests:
pytest test_game.py
"""

import numpy as np

import log_handler
from curling import board as board_utils
from curling import constants as c
from curling import game
from curling import simulation
from curling import utils


def test_simulation_setupBoard_0():
    sim = simulation.Simulation()

    stones = list(sim.getStones())
    assert len(stones) == 0


def test_simulation_setupBoard_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    sim = curl.sim
    sim.setupBoard(board)
    sim.addStone(c.P1_COLOR, 0, utils.TEE_LINE)
    sim.addStone(c.P2_COLOR, 0, utils.TEE_LINE)

    stones = list(sim.getStones())
    assert len(stones) == 2


def test_simulation_getNextStoneId():
    curl = game.CurlingGame()
    r = utils.STONE_RADIUS

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 0  # for red

    curl.sim.addStone(c.P1_COLOR, 0, utils.HOG_LINE)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 0  # for blue

    curl.sim.addStone(c.P2_COLOR, 2 * r, utils.HOG_LINE + 2 * r)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 1  # for red

    curl.sim.addStone(c.P1_COLOR, 4 * r, utils.HOG_LINE + 4 * r)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 1  # for blue


def test_simulation_getNextStoneId_with_removed():
    curl = game.CurlingGame()
    curl.sim.addShooterAsInvalid()
    curl.sim.addShooterAsInvalid()
    curl.sim.addShooterAsInvalid()
    curl.sim.addShooterAsInvalid()
    r = utils.STONE_RADIUS

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 2  # for red

    curl.sim.addStone(c.P1_COLOR, 0, utils.HOG_LINE)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 2  # for blue

    curl.sim.addStone(c.P2_COLOR, 2 * r, utils.HOG_LINE + 2 * r)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 3  # for red

    curl.sim.addStone(c.P1_COLOR, 4 * r, utils.HOG_LINE + 4 * r)

    i = simulation.getNextStoneId(curl.sim.getBoard())
    assert i == 3  # for blue


@log_handler.on_error()
def test_simulation_getBoard_is_symmetric():
    """Create a board then convert it to simulation and back to board."""
    curl = game.CurlingGame()
    expected = curl.sim.getBoard()

    curl.sim.addStone(c.P1_COLOR, 0, utils.TEE_LINE)

    curl.sim.setupBoard(expected)
    actual = curl.sim.getBoard()

    actual_position = list(board_utils.get_xy_team1(actual))
    expected_position = list(board_utils.get_xy_team1(expected))
    np.testing.assert_array_equal(actual_position, expected_position)


def SKIP_test_simulation_getBoard_button():
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


def SKIP_test_simulation_getBoard_right_edge():
    sim = game.CurlingGame().sim

    board = sim.getBoard()
    board[-1][0] = c.EMPTY

    button_x, button_y = game.BUTTON_POSITION
    button_x -= utils.dist(inches=10)  # NOTE - shifting to the left
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


def test_invalid_shooter():
    curl = game.CurlingGame()
    curl.sim.addShooterAsInvalid()
