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
    assert utils.realToBoard(*utils.boardToReal(0,0)) == (0.0, 0.0)
    assert utils.realToBoard(*utils.boardToReal(1,1)) == (1.0, 1.0)
    assert utils.realToBoard(*utils.boardToReal(-33,-66)) == (-33.0, -66.0)

    assert utils.boardToReal(*utils.realToBoard(0,0)) == (0.0, 0.0)
    assert utils.boardToReal(*utils.realToBoard(1,1)) == (1.0, 1.0)
    assert utils.boardToReal(*utils.realToBoard(-33,-66)) == (-33.0, -66.0)
