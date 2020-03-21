import numpy as np


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
            print('\nMoves:', [i for (i, valid) in enumerate(valid_moves) if valid])
            try:
                move = int(input())
                valid_moves[move]
                break
            except KeyboardInterrupt:
                raise
            except:
                print('Invalid move')
        return move
