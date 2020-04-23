import logging
import numpy as np

from curling import simulation
from curling import utils
from curling import constants as c

log = logging.getLogger(__name__)

BUTTON_POSITION = utils.pymunk.Vec2d(0, utils.dist(feet=124.5))  # TODO: MOVE IT OUT OF HERE


class CurlingGame:

    def __init__(self):
        self.sim = simulation.Simulation(self.getBoardSize())

    def getInitBoard(self):
        return utils.getInitBoard()

    def getBoardSize(self):
        board_size = utils.getBoardSize()
        assert board_size[0] >= 16  # need at least this size for data
        return board_size

    def getActionSize(self):
        return len(c.ACTION_LIST)

    def getNextState(self, board, player, action):
        log.debug(f'getNextState(board, {player}, {action})')
        self.sim.setupBoard(board)
        self.sim.setupAction(player, action)
        self.sim.run()

        next_board = self.sim.getBoard()
        next_player = 0 - player
        log.debug(f'  return board, {next_player}')
        return next_board, next_player

    def getValidMoves(self, board, player):

        if self._thrownStones(board) >= 16:
            data_row = board[-1][0:16]
            log.warning('getValidMoves() requested at game end. Data: %s' % data_row)
            return [0] * self.getActionSize()

        player_turn = utils.getNextPlayer(board, player)
        if player_turn == player:
            return [1] * self.getActionSize()  # all moves are valid

        return [0] * self.getActionSize()

    def getGameEnded(self, board, player):
        if self._thrownStones(board) < 16:
            return 0

        self.sim.setupBoard(board)

        house_radius = utils.dist(feet=6, inches=c.STONE_RADIUS_IN)
        stones = self.sim.getStones()

        # TODO: Optimization - don't compute euclid twice
        near_button = sorted(stones, key=lambda s: utils.euclid(s.body.position, BUTTON_POSITION))
        in_house = list(filter(lambda s: utils.euclid(s.body.position, BUTTON_POSITION) < house_radius, near_button))

        if len(in_house) == 0:
            # Draw is better than being forced to 1
            return 0.5

        win_color = in_house[0].color
        win_count = 0
        while len(in_house) > win_count and in_house[win_count].color == win_color:
            win_count += 1

        hammer_won = (win_color == c.P2_COLOR)

        log.debug(f'Win count: {win_count}, color: {win_color}, hammer won: {hammer_won}')

        if hammer_won:
            if win_count == 1:
                # This is almost as bad as losing
                return -0.5
            # 2 or more stones is a great win
            return win_count

        # a steal is always good
        return win_count * -1

    def _thrownStones(self, board):
        stones = self.sim.getStones()
        data_row = board[-1][0:16]
        p1_oop = len(np.argwhere(data_row == c.P1_OUT_OF_PLAY))
        p2_oop = len(np.argwhere(data_row == c.P2_OUT_OF_PLAY))
        thrown_stones = len(stones) + p1_oop + p2_oop
        log.debug(f'getGameEnded() -> {thrown_stones}')
        return thrown_stones

    @staticmethod
    def getCanonicalForm(board, player):
        log.debug(f'getCanonicalForm({board[-1][0:16]}, {player})')
        if player == c.P1:
            log.debug(f'getCanonicalForm(board, {player}) -> {board[-1][0:16]}')
            return board

        flip = board * -1

        # Data row remains the same
        flip[-1][0:8] = (board[-1][8:16] * -1)
        flip[-1][8:16] = (board[-1][0:8] * -1)
        log.debug(f'getCanonicalForm(board, {player}) -> {flip[-1][0:16]}')
        return flip

    @staticmethod
    def getSymmetries(board, pi):
        # TODO: this can be flipped over y axis
        return [(board, pi)]

    @staticmethod
    def stringRepresentation(board):
        return str(utils.getBoardRepr(board))

    @staticmethod
    def display(board):
        print(" -----------------------")
        print(list(np.argwhere(board == c.P1)))
        print(list(np.argwhere(board == c.P2)))
        print(" -----------------------")


# url: left 0 right: 396
# pymunk: left: -84 right: 84

# url top 12: 392.5 back 12: 700.5
# pymunk: top 12: 1416.0 back 12: 1560.0


def url_to_x(x):
    v = float(x) * 0.424 - 84
    return str(int(v * 100) / 100)


def url_to_y(y):
    v = float(y) * 0.462 + 1232
    return str(int(v * 100) / 100)


def x_to_url(x):
    v = (float(x) + 84) / 0.424
    return str(int(v * 100) / 100)


def y_to_url(y):
    v = (float(y) - 1232) / 0.462
    return str(int(v * 100) / 100)


def getUrl(board):
    team1 = zip(board[0:8], board[8:16])
    team2 = zip(board[16:24], board[24:32])
    return (
            'blue=' + '|'.join(x_to_url(x) + ',' + y_to_url(y) for x, y in team2 if 1 < float(y) < 2000) +
            '&red=' + '|'.join(x_to_url(x) + ',' + y_to_url(y) for x, y in team1 if 1 < float(y) < 2000)
    )
