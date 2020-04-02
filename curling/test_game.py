"""
To run tests:
pytest test_game.py
"""

import numpy as np
import pymunk

from . import game
from . import simulation


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

def test_simulation_setupBoard():
    board = np.zeros(40)
    board[0] = 1
    board[8] = 2

    board[16] = 3
    board[24] = 4

    sim = simulation.Simulation()
    sim.setupBoard(board)
    stones = list(sim.getStones())
    assert len(stones) == 2

def test_simulation_setupBoard_2():
    board = np.zeros(40)
    board[0] = 0
    board[8] = 0

    board[16] = 5000
    board[24] = 5000

    sim = simulation.Simulation()
    sim.setupBoard(board)
    stones = list(sim.getStones())
    assert len(stones) == 1

def test_simulation_getNextStoneId():
    sim = simulation.Simulation()

    i = simulation.getNextStoneId( sim.getBoard() )
    assert i == 0  # for red

    sim.addStone(simulation.TEAM_1_COLOR, 20, 30)

    i = simulation.getNextStoneId( sim.getBoard() )
    assert i == 0  # for blue

    sim.addStone(simulation.TEAM_2_COLOR, 30, 40)

    i = simulation.getNextStoneId( sim.getBoard() )
    assert i == 1  # for red

    sim.addStone(simulation.TEAM_1_COLOR, 40, 50)

    i = simulation.getNextStoneId( sim.getBoard() )
    assert i == 1  # for blue

def test_simulation_setupBoard():
    sim = simulation.Simulation()

    expected = np.zeros(40)
    expected[0] = 1
    expected[8] = 2

    expected[16] = 3
    expected[24] = 4

    expected[1] = 5
    expected[9] = 6

    expected[17] = 7
    expected[25] = 8

    sim.setupBoard(expected)

    stones = list(sim.getStones())
    print(stones)

    print('Testing setupBoard()')
    actual = sim.getBoard()

    assert list(actual) == list(expected)

    
