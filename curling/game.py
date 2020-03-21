import sys
import numpy as np

sys.path.append('..')
from Game import Game

def getNextStoneIds(board, player):
    offset = 0 if player == 1 else 16

    last_stone = offset
    for x in range(offset, offset + 8):
        # Check Y for team 1 and team 2.
        if board[x + 8] > 0:  # y for a player is 8 ahead of its x
            last_stone = x + 1

    nx = last_stone
    ny = last_stone + 8
    return nx, ny


class CurlingGame(Game):

    def __init__(self):
        Game.__init__(self)

    def getInitBoard(self):
        # x = 0 means center line. view from thrower. -6 means Skip's right
        b = np.zeros(40)
        return b

    def getBoardSize(self):
        # 2: x and y coordinates. 16: total stones.
        # index 0 will be x for team 1
        # index 1 will be y for team 1
        # index 2 will be x for team 2
        # index 3 will be y for team 2
        # index 4 not used
        return (5, 8)

    def getActionSize(self):
        return 3  # guard, draw, takeout. No broom change

    def getNextState(self, board, player, action):
        if action == 0:  # TODO: Figure out enumeration -.-"
            # a guard
            x = 0
            y = 112

        if action == 1:
            # a draw
            x = 0
            y = 120

        if action == 2:
            # a takeout
            x = 0
            y = 130

        ix, iy = getNextStoneIds(board, player)
        newboard = board.copy()
        newboard[ix] = x
        newboard[iy] = y

        next_player = 0 - player
        return newboard, next_player

    def getValidMoves(self, board, player):
        return [1] * self.getActionSize()  # all moves are valid

    def getGameEnded(self, board, player):
        nx, ny = getNextStoneIds(board, 1)
        if nx < 8:
            return 0

        p1_score = sum([int(y == 120) for y in board[8:15]])
        p2_score = sum([int(y == 120) for y in board[24:31]])

        if player != 1:
            p1_score, p2_score = p2_score, p1_score

        if p1_score > p2_score:
            return 1
        if p1_score < p2_score:
            return -1
        return 0.0001

    def getCanonicalForm(self, board, player):
        # Check if this needs to be changed by switching rows 01 and 23
        return board

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def stringRepresentation(self, board):
        return str(list(board))

    @staticmethod
    def display(board):
        print(" -----------------------")
        print(board[0:8])
        print(board[8:16])
        print(board[16:24])
        print(board[24:32])
        print(" -----------------------")
