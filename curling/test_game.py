from unittest import mock

import numpy as np

import curling.utils
import log_handler
from . import constants as c
from . import game
from . import utils


def test_board_is_2d():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    width, height = board.shape
    assert width >= 16  # Minimum for data row
    assert height > width  # just sanity check


def test_getNextPlayer_0():
    curl = game.CurlingGame()
    player = curling.utils.getNextPlayer(curl.getInitBoard(), c.P1)
    assert player == 1


def test_getNextPlayer_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    player = curling.utils.getNextPlayer(board, c.P1)
    assert player == -1


def test_getNextPlayer_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    board[-1][8] = c.EMPTY

    player = curling.utils.getNextPlayer(board, c.P1)
    assert player == 1


def test_getNextPlayer_3():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    board[-1][8] = c.EMPTY

    board[-1][1] = c.EMPTY

    player = curling.utils.getNextPlayer(board, c.P1)
    assert player == -1


def test_getNextPlayer_4():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    board[-1][8] = c.EMPTY

    board[-1][1] = c.EMPTY
    board[-1][9] = c.EMPTY

    player = curling.utils.getNextPlayer(board, c.P1)
    assert player == 1


def test_getNextPlayer_4_canonical():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    board[-1][8] = c.EMPTY

    board[-1][1] = c.EMPTY
    board[-1][9] = c.EMPTY

    canon = curl.getCanonicalForm(board, c.P2)
    player = curling.utils.getNextPlayer(canon, c.P2)
    assert player == -1


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

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:16] = [c.P2_OUT_OF_PLAY] * 8
    ended = curl.getGameEnded(board, 1)

    assert ended == 0.00001  # Draw


@log_handler.on_error()
def test_gameEnded_HammerWinsBy1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    curl.sim.addStone(c.P2_COLOR, *game.BUTTON_POSITION)
    board = curl.sim.getBoard()

    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


@log_handler.on_error()
def test_gameEnded_HammerWinsBy2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][14:15] = c.EMPTY

    x, y = game.BUTTON_POSITION
    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    curl.sim.addStone(c.P2_COLOR, x - 5, y - 5)
    curl.sim.addStone(c.P2_COLOR, x + 5, y + 5)
    board = curl.sim.getBoard()

    ended = curl.getGameEnded(board, c.P2)

    assert ended == 2  # Win by 2 is good


def test_gameEnded_SlightlyOffCenter_y_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    x, y = game.BUTTON_POSITION
    curl.sim.addStone(c.P2_COLOR, x, y - utils.dist(inches=1))

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, 1)

    assert ended == -1


def test_gameEnded_SlightlyOffCenter_y_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    x, y = game.BUTTON_POSITION
    curl.sim.addStone(c.P2_COLOR, x, y + utils.dist(inches=1))

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, 1)

    assert ended == -1


def test_gameEnded_x_HammerCloser():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:7] = [c.P1_OUT_OF_PLAY] * 7
    board[-1][7] = c.EMPTY

    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    curl.sim.setupBoard(board)

    x, y = game.BUTTON_POSITION
    curl.sim.addStone(c.P1_COLOR, x + utils.dist(inches=10), y)
    curl.sim.addStone(c.P2_COLOR, x - utils.dist(inches=1), y)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


def test_gameEnded_y_HammerCloser():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:7] = [c.P1_OUT_OF_PLAY] * 7
    board[-1][7] = c.EMPTY

    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    curl.sim.setupBoard(board)

    x, y = game.BUTTON_POSITION
    curl.sim.addStone(c.P1_COLOR, x, y - utils.dist(inches=10))
    curl.sim.addStone(c.P2_COLOR, x, y + utils.dist(inches=1))

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1


def test_gameEnded_SlightlyOffCenter_x_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    x, y = game.BUTTON_POSITION
    stone = curl.sim.addStone(c.P2_COLOR, x - utils.dist(inches=1), y)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, c.P2)

    assert ended == 1, (np.argwhere(board == c.P2), (x, y), stone.body.position)


def test_gameEnded_SlightlyOffCenter_x_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7
    board[-1][15] = c.EMPTY

    # Team 2 is winning by 1
    curl.sim.setupBoard(board)
    x, y = game.BUTTON_POSITION
    curl.sim.addStone(c.P2_COLOR, x + utils.dist(inches=1), y)

    board = curl.sim.getBoard()
    ended = curl.getGameEnded(board, 1)

    assert ended == -1


@log_handler.on_error()
def test_gameEnded_OpponentWinsBy1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:7] = [c.P1_OUT_OF_PLAY] * 7
    board[-1][7] = c.EMPTY

    board[-1][8:16] = [c.P2_OUT_OF_PLAY] * 8

    # Team 1 is winning by 1
    curl.sim.setupBoard(board)
    curl.sim.addStone(c.P1_COLOR, *game.BUTTON_POSITION)
    board = curl.sim.getBoard()

    ended = curl.getGameEnded(board, -1)

    assert ended == -1


def test_gameEnded_NotEndOfGame():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    board[-1][0:8] = [c.P1_OUT_OF_PLAY] * 8
    board[-1][8:15] = [c.P2_OUT_OF_PLAY] * 7

    # Hammer hasn't been thrown yet
    board[-1][15] = c.P2_NOT_THROWN

    ended = curl.getGameEnded(board, 1)

    assert ended == 0


def test_gameEnded_edgeCase():
    # Ensure the board is setup/reset before counting the stones
    # This edge case is when a game goes in "reverse" because of MCTS

    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0:7] = [c.P1_OUT_OF_PLAY] * 7
    board[-1][8:16] = [c.P2_OUT_OF_PLAY] * 8

    assert curl.getGameEnded(board, 1) == 0

    board[-1][7] = c.EMPTY
    board[2][2] = c.P1

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


@mock.patch("curling.constants.ACTION_LIST", c.SHORT_ACTION_LIST)
def test_get_valid_moves_caches():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    with mock.patch.object(curl.sim, 'run', wraps=curl.sim.run) as spy:
        curl.getValidMoves(board, 1)
        assert spy.call_count == 4

        curl.getValidMoves(board, 1)
        assert spy.call_count == 4  # Call count didn't increase!
