import logging
from unittest import mock

import numpy as np

import log_handler
from curling import board as board_utils
from curling import constants as c
from curling import game
from curling import utils

log = logging.getLogger(__name__)


def test_getNextPlayer_0():
    curl = game.CurlingGame()
    player = utils.getNextPlayer(curl.getInitBoard(), c.P1)
    assert player == 1


def test_getNextPlayer_1():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))

    total_stones = len(curl.sim.getStones())

    assert total_stones == 1
    assert next_player == c.P2


def test_getNextPlayer_2():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))

    total_stones = len(curl.sim.getStones())

    assert total_stones == 2
    assert next_player == c.P1


def test_getNextPlayer_3():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))

    total_stones = len(curl.sim.getStones())

    assert total_stones == 3
    assert next_player == c.P2



def test_getNextPlayer_4():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))
    next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, '3', 5)))

    total_stones = len(curl.sim.getStones())

    assert total_stones == 4
    assert next_player == c.P1


def test_getNextPlayer_4_canonical():
    curl = game.CurlingGame()
    board = curl.getInitBoard()
    board[-1][0] = c.EMPTY
    board[-1][8] = c.EMPTY

    board[-1][1] = c.EMPTY
    board[-1][9] = c.EMPTY

    canon = curl.getCanonicalForm(board, c.P2)
    player = utils.getNextPlayer(canon, c.P2)
    assert player == -1


def test_guard():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 5)))

    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert shooter.is_guard


def test_draw():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '7', 6)))

    p1_stones = len(list(board_utils.get_xy_team1(next_board)))

    assert p1_stones == 1
    assert next_player == c.P2

    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert not shooter.is_guard


def test_control():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, 'control', 6)))

    p1_stones = len(list(board_utils.get_xy_team1(next_board)))

    assert p1_stones == 0
    assert next_player == c.P2


def test_5_rock_rule():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    # Set up a guard
    next_board, next_player = curl.getNextState(board, c.P1, c.ACTION_LIST.index((1, '3', 6)))
    assert next_player == c.P2
    shooter = curl.sim.getStones()[0]
    shooter.updateGuardValue()  # We normally only do this during addStone()
    assert shooter.is_guard

    # Take it out
    with mock.patch.object(curl.sim, 'addShooterAsInvalid', wraps=curl.sim.addShooterAsInvalid) as spy:
        next_board, next_player = curl.getNextState(next_board, next_player, c.ACTION_LIST.index((1, 'control', 0)))
        assert spy.call_count == 1
    assert next_player == c.P1

    p1_stones = len(list(board_utils.get_xy_team1(next_board)))
    assert p1_stones == 1, "Player 1 should keep their stone."

    p2_stones = len(list(board_utils.get_xy_team2(next_board)))
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

    p1_stones = len(list(board_utils.get_xy_team1(next_board)))
    assert p1_stones == 1, "Player 1 should keep their stone."

    p2_stones = len(list(board_utils.get_xy_team2(next_board)))
    assert p2_stones == 0, "Player 2 should have had their stone removed."

    first_stone = curl.sim.getStones()[0]
    assert first_stone.is_guard


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


def test_two_wall_collision():
    # TODO this would actually be a good test to have.
    pass
    # bs = "1:[]:2:[[28, 59]]:d:[3, 3, 3, 3, 2, 2, 2, 2, -3, -3, -3, 0, -2, -2, -2, -2]"
    #
    # curl = game.CurlingGame()
    # curl.getNextState(curl.boardFromString(bs), 1, 178)

def test_getNextState_has_extra_data():
    curl = game.CurlingGame()
    board = curl.getInitBoard()

    next_board, _ = curl.getNextState(board, c.P1, utils.getAction(-1, '5', -1))

    np.testing.assert_almost_equal(
        next_board[:,0],
        [70.3, 1450, 1, 1, 81.2, 1],
        decimal=-1
    )
