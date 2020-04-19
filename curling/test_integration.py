import logging

import numpy as np

from . import constants as c
from . import game

logging.basicConfig(level=logging.DEBUG)


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
