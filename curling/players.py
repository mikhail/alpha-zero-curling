import numpy as np
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
        valid_moves = self.game.getValidMoves(board, 1)
        while True:
            # print('\nMoves:', [i for (i, valid) in enumerate(valid_moves) if valid])
            print('\n Weight / Handle (-1,1) / Broom:', end=' ')
            move = input()
            weight, handle, broom = move.split(' ')
            try:
                action = utils.ACTION_LIST.index( (int(handle), weight, int(broom)) )
                break
            except KeyboardInterrupt:
                raise
            except:
                print('Invalid move')
                print('Weights: ', utils.WEIGHT_FT.keys())
                print('Brooms: %s - %s' % (min(utils.BROOMS), max(utils.BROOMS)))
        return action
