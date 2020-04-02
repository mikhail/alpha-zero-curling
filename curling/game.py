import numpy as np
import sys

sys.path.append('..')
from Game import Game as AbstractGameClass

from curling import simulation
from curling import utils

def getNextPlayer(board):

    last_p1 = 0
    for y in range(8,16):
        if board[y] > 0:
            last_p1 = y - 7

    last_p2 = 0
    for y in range(24,32):
        if board[y] > 0:
            last_p2 = y - 23

    if last_p1 > last_p2:
        return -1

    return 1


class CurlingGame(AbstractGameClass):

    def __init__(self):
        AbstractGameClass.__init__(self)
        self.sim = simulation.Simulation()

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
        # index 4: not used
        return (5, 8)

    def getActionSize(self):
        return len(utils.ACTION_LIST)

    def getNextState(self, board, player, action):
        self.sim.setupBoard(board)
        self.sim.setupAction(player, action)
        self.sim.run()

        next_board = self.sim.getBoard()
        next_player = 0 - player

        return next_board, next_player

    def getValidMoves(self, board, player):
        player_turn = getNextPlayer(board)
        if player_turn == player:
            return [1] * self.getActionSize()  # all moves are valid

        return [0] * self.getActionSize()

    def getGameEnded(self, board, player):
        if board[25] < 1:
            return 0

        self.sim.setupBoard(board)
        stones = self.sim.getStones()

        button = utils.pymunk.Vec2d(0, utils.dist(feet=124.5))
        # Optimization - don't compute euclid twice
        # add radius of stone to 6ft measurement
        near_button = sorted(stones, key=lambda s: utils.euclid(s.body.position, button))
        in_house = list(filter(lambda s:  utils.euclid(s.body.position, button) < utils.dist(feet=6), near_button))
        if len(in_house) == 0:
            return 0.001

        win_color = in_house[0].color
        # XXX: single-end simulation doesn't care about total count
        return 1 if win_color == utils.TEAM_1_COLOR else -1

    def getCanonicalForm(self, board, player):
        if player == 1:
            return board

        switched_board = self.getInitBoard()
        switched_board[0:16] = board[16:32]
        switched_board[16:32] = board[0:16]

        return switched_board


    def getSymmetries(self, board, pi):
        # TODO: this can be flipped over y axis
        # all same-color stones can have full permutation
        return [(board, pi)]

    def stringRepresentation(self, board):
        return str(utils.getRoundedBoard(board))

    @staticmethod
    def display(board):
        print(" -----------------------")
        print([f'{p:2.2f}' for p in board[0:8]])
        print([f'{p:2.2f}' for p in board[8:16]])
        print([f'{p:2.2f}' for p in board[16:24]])
        print([f'{p:2.2f}' for p in board[24:32]])
        print(" -----------------------")
