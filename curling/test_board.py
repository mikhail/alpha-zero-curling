import numpy as np

from curling import board
from curling import constants as c


def test_update_distance_and_score():
  b = board.getInitBoard()
  board.set_stone(b, c.P1, 0, c.BUTTON_POSITION.x + 1, c.BUTTON_POSITION.y + 1)
  board.update_distance_and_score(b)

  assert 1.41 < b[c.BOARD_DISTANCE][0] < 1.42
  assert b[c.BOARD_SCORING][0] == c.SCORING

def test_correct_stones_scoring_1():
  b = board.getInitBoard()
  board.set_stone(b, c.P1, 0, c.BUTTON_POSITION.x + 1, c.BUTTON_POSITION.y + 1)
  board.set_stone(b, c.P1, 1, c.BUTTON_POSITION.x + 2, c.BUTTON_POSITION.y + 2)
  board.set_stone(b, c.P1, 2, c.BUTTON_POSITION.x + 3, c.BUTTON_POSITION.y + 3)

  board.set_stone(b, c.P2, 0, c.BUTTON_POSITION.x + 4, c.BUTTON_POSITION.y + 4)

  board.set_stone(b, c.P1, 4, c.BUTTON_POSITION.x + 5, c.BUTTON_POSITION.y + 5)

  board.update_distance_and_score(b)

  assert np.sum(b[c.BOARD_SCORING]) == 3

def test_correct_stones_scoring_2():
  b = board.getInitBoard()
  board.set_stone(b, c.P2, 0, c.BUTTON_POSITION.x + 1, c.BUTTON_POSITION.y + 1)
  board.set_stone(b, c.P2, 1, c.BUTTON_POSITION.x + 2, c.BUTTON_POSITION.y + 2)
  board.set_stone(b, c.P2, 2, c.BUTTON_POSITION.x + 3, c.BUTTON_POSITION.y + 3)

  board.set_stone(b, c.P1, 0, c.BUTTON_POSITION.x + 4, c.BUTTON_POSITION.y + 4)

  board.set_stone(b, c.P2, 4, c.BUTTON_POSITION.x + 5, c.BUTTON_POSITION.y + 5)

  board.update_distance_and_score(b)

  assert np.sum(b[c.BOARD_SCORING]) == 3