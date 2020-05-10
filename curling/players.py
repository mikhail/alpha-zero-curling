import numpy as np

import curling.constants
from curling import utils


class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a] != 1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):

        while True:
            print('\n Weight / Handle (-1,1) / Broom:', end=' ')
            move = input()
            weight, handle, broom = move.split(' ')
            try:
                action = utils.getAction(handle, weight, broom)
                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print('Invalid move: ', e)
                print('Weights: ', curling.constants.WEIGHT_FT.keys())
                print('Brooms: %s - %s' % (min(curling.constants.BROOMS), max(curling.constants.BROOMS)))
        return action
