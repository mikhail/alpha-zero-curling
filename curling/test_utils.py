import numpy as np

from curling import constants as c
from curling import utils


def test_get_board_repr_empty():
    string = utils.getBoardRepr(np.zeros((5, 5)))

    assert string == '1:[]:2:[]:d:[0, 0, 0, 0, 0]'


def test_get_board_repr_teams():
    board = np.zeros((5, 5))
    board[0][0] = c.P1
    board[2][2] = c.P2
    string = utils.getBoardRepr(board)

    assert string == '1:[[0, 0]]:2:[[2, 2]]:d:[0, 0, 0, 0, 0]'


def test_real_to_board_and_back():
    assert utils.realToBoard(*utils.boardToReal(0, 0)) == (0.0, 0.0)
    assert utils.realToBoard(*utils.boardToReal(1, 1)) == (1.0, 1.0)
    assert utils.realToBoard(*utils.boardToReal(-33, -66)) == (-33.0, -66.0)

    assert utils.boardToReal(*utils.realToBoard(0, 0)) == (0.0, 0.0)
    assert utils.boardToReal(*utils.realToBoard(1, 1)) == (1.0, 1.0)
    assert utils.boardToReal(*utils.realToBoard(-33, -66)) == (-33.0, -66.0)


def test_five_rock_rule_first():
    takeout = utils.newStone(c.P1_COLOR)
    space = utils.Space()
    space.get_stones = lambda: []
    space.shooter_color = c.P1_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_second():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 1
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is True


def test_five_rock_rule_fifth():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 5
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is True


def test_five_rock_rule_sixth():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 6
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_not_guard():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = False
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 1
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_not_all_inplay():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = False
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 2
    space.p1_removed_stones = 2
    space.p2_removed_stones = 2
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False
