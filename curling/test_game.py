import logging
from unittest import mock

import numpy as np

import log_handler
from curling import board as board_utils
from curling import constants as c
from curling import game
from curling import utils

inch = utils.dist(inches=1)


def test_board_is_2d():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    height, width = board.shape
    assert width == 16
    assert height == 4


def test_CanonicalBoard_changed():
    curl = game.CurlingGame()
    original = curl.getInitBoard()
    original[1][1] = 1

    canonical = curl.getCanonicalForm(original, 1)

    np.testing.assert_array_equal(canonical, original)


def test_gameEnded_GameNotStarted():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    ended = curl.getGameEnded(board, 1)

    assert ended == 0


def test_gameEnded_NoStonesInPlay():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)
    ended = curl.getGameEnded(board, 1)

    assert ended == 0.00001  # Draw


@log_handler.on_error()
def test_gameEnded_HammerWinsBy1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.configure_hammer_1_scenario(board)

    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


@log_handler.on_error()
def test_gameEnded_HammerWinsBy2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.configure_hammer_2_scenario(board)

    ended = curl.getGameEnded(board, c.P2)

    assert ended == 2  # Win by 2 is good


def test_gameEnded_SlightlyOffCenter_y_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION
    # Team 2 is winning by 1
    board_utils.set_stone(board, c.P2, 7, x, y - 1 * inch)
    curl.sim.setupBoard(board)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, 1)

    assert ended == -1


def test_gameEnded_SlightlyOffCenter_y_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION
    # Team 2 is winning by 1
    board_utils.set_stone(board, c.P2, 7, x, y + 1 * inch)
    curl.sim.setupBoard(board)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, 1)

    assert ended == -1


def test_gameEnded_x_HammerCloser():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION

    board_utils.set_stone(board, c.P1, 7, x, y + 10 * inch)
    board_utils.set_stone(board, c.P2, 7, x, y - 1 * inch)
    curl.sim.setupBoard(board)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


def test_gameEnded_y_HammerCloser():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION

    board_utils.set_stone(board, c.P1, 7, x, y - 10 * inch)
    board_utils.set_stone(board, c.P2, 7, x, y + 1 * inch)
    curl.sim.setupBoard(board)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


def test_gameEnded_SlightlyOffCenter_x_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION
    # Team 2 is winning by 1
    board_utils.set_stone(board, c.P2, 7, x - 1 * inch, y)
    curl.sim.setupBoard(board)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


def test_gameEnded_SlightlyOffCenter_x_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)

    x, y = game.BUTTON_POSITION
    # Team 2 is winning by 1
    board_utils.set_stone(board, c.P2, 7, x + 1 * inch, y)

    ended = curl.getGameEnded(board, 1)

    assert ended == -1


def test_gameEnded_NotEndOfGame():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)
    board_utils.set_stone(board, c.P2, 7, 0,0, c.NOT_THROWN, c.IN_PLAY)

    ended = curl.getGameEnded(board, 1)

    assert ended == 0


def test_gameEnded_edgeCase():
    # Ensure the board is setup/reset before counting the stones
    # This edge case is when a game goes in "reverse" because of MCTS

    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board_utils.scenario_all_out_of_play(board)
    board_utils.set_stone(board, c.P2, 7, 0,0, c.NOT_THROWN, c.IN_PLAY)

    assert curl.getGameEnded(board, 1) == 0

    board_utils.set_stone(board, c.P2, 7, 0,0, c.THROWN, c.OUT_OF_PLAY)

    assert curl.getGameEnded(board, 1) != 0


def test_display():
    curl = game.CurlingGame()
    curl.display(curl.getInitBoard())


@mock.patch("curling.constants.ACTION_LIST", c.SHORT_ACTION_LIST)
def test_get_valid_moves():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    valid = curl.getValidMoves(board, 1)

    assert sum(valid) < len(c.ACTION_LIST)
    assert sum(valid) == 2


# NOTE: Commented out because it's really slow.
# @mock.patch("curling.constants.ACTION_LIST", c.SHORT_ACTION_LIST)
# def test_get_valid_moves_caches():
#     curl = game.CurlingGame()
#     board = curl.getInitBoard()
#
#     with mock.patch.object(curl.sim, 'run', wraps=curl.sim.run) as spy:
#         curl.getValidMoves(board, 1)
#         assert spy.call_count == 4
#
#         curl.getValidMoves(board, 1)
#         assert spy.call_count == 4  # Call count didn't increase!