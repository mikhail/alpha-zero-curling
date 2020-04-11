"""
To run tests:
pytest test_game.py
"""

import numpy as np
import pymunk

from . import game
from . import simulation
from . import utils


def test_getNextPlayer_0():
    player = game.getNextPlayer(np.zeros(40))
    assert player == 1

def test_getNextPlayer_1():
    board = np.zeros(40)
    board[0] = -6
    board[8] = 126
    player = game.getNextPlayer(board)
    assert player == -1

def test_getNextPlayer_2():
    board = np.zeros(40)
    board[0] = -6
    board[8] = 126

    board[16] = -6
    board[24] = 126
    player = game.getNextPlayer(board)
    assert player == 1

def test_getNextPlayer_3():
    board = np.zeros(40)
    board[0] = -6
    board[8] = 126

    board[16] = -6
    board[24] = 126

    board[1] = -6
    board[9] = 126
    player = game.getNextPlayer(board)
    assert player == -1

def test_getNextPlayer_4():
    board = np.zeros(40)
    board[0] = -6
    board[8] = 126

    board[16] = -6
    board[24] = 126

    board[1] = -6
    board[9] = 126

    board[17] = -6
    board[25] = 126

    player = game.getNextPlayer(board)
    assert player == 1

def test_CanonicalBoard():
    board = np.zeros(40)
    board[0] = 1
    board[8] = 2

    board[16] = 3
    board[24] = 4

    curling = game.CurlingGame()
    actual = curling.getCanonicalForm(board, -1)

    expected = np.zeros(40)
    expected[16] = 1
    expected[24] = 2
    expected[0] = 3
    expected[8] = 4

    assert list(actual) == list(expected)

def test_gameEnded_1():
    board = np.zeros(40)

    curling = game.CurlingGame()

    ended = curling.getGameEnded(board, 1)

    assert ended == 0

def test_gameEnded_2():
    board = np.full(40, utils.INVALID_VALUE)  # all stones out of the game

    curling = game.CurlingGame()

    ended = curling.getGameEnded(board, 1)

    assert ended == 0.5  # Draw

def test_gameEnded_3():
    board = np.full(40, utils.INVALID_VALUE)  # all stones out of the game
    # Team 1 is winning
    board[0] = 0
    board[8] = utils.dist(feet=124.5)

    curling = game.CurlingGame()

    ended = curling.getGameEnded(board, 1)

    assert ended == -0.5

def test_gameEnded_4():
    board = np.full(40, utils.INVALID_VALUE)  # all stones out of the game
    # Team 2 is winning
    board[16] = 0
    board[24] = utils.dist(feet=124.5)

    curling = game.CurlingGame()

    ended = curling.getGameEnded(board, 1)

    assert ended == -1

def test_gameEnded_5():
    board = np.full(40, utils.INVALID_VALUE)  # all stones out of the game
    # Except the hammer
    board[23] = 0
    board[31] = 0

    curling = game.CurlingGame()

    ended = curling.getGameEnded(board, 1)

    assert ended == 0
