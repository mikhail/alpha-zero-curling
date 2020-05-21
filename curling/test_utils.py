import numpy as np

import log_handler
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


def test_board_to_real():
    c.BOARD_RESOLUTION = 1

    left_wall = -utils.ICE_WIDTH / 2
    right_wall = utils.ICE_WIDTH / 2
    board_max_x, board_max_y = utils.getBoardSize()
    board_max_y -= 1  # Ignore the data layer

    radius = utils.STONE_RADIUS
    assert all(
        np.isclose(
            utils.boardToReal(0, 0),
            (left_wall + radius, utils.HOG_LINE + radius),
            rtol=c.BOARD_RESOLUTION))

    rx, ry = utils.boardToReal(board_max_x, board_max_y)
    ex, ey = (right_wall - radius, utils.BACKLINE_ELIM - radius)
    assert np.isclose(rx, ex, rtol=c.BOARD_RESOLUTION)
    assert np.isclose(ry, ey, rtol=c.BOARD_RESOLUTION)


@log_handler.on_error()
def test_real_to_board():
    c.BOARD_RESOLUTION = 1

    left_wall = -utils.ICE_WIDTH / 2
    right_wall = utils.ICE_WIDTH / 2
    board_max_x, board_max_y = utils.getBoardSize()
    board_max_x -= 1  # Ignore the data layer

    radius = utils.STONE_RADIUS
    assert utils.realToBoard(left_wall + radius, utils.HOG_LINE + radius) == (0, 0)

    assert utils.realToBoard(right_wall - radius, utils.BACKLINE_ELIM - radius) == (board_max_x - 1, board_max_y - 1)


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


def test_proper_round():
    assert utils.proper_round(0) == 0
    assert utils.proper_round(0.4999999) == 0
    assert utils.proper_round(0.5) == 1
    assert utils.proper_round(0.500000001) == 1
    assert utils.proper_round(0.999999999) == 1
    assert utils.proper_round(1.5) == 2
