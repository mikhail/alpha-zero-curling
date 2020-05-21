import json
import logging

import numpy as np

from curling import constants as c
from curling import simulation
from curling import utils

log = logging.getLogger(__name__)

BUTTON_POSITION = utils.pymunk.Vec2d(0, utils.dist(feet=124.5))  # TODO: MOVE IT OUT OF HERE


class GameException(Exception):
    """Logic within game is broken."""


class CurlingGame:

    def __init__(self):
        self.sim = simulation.Simulation(self.getBoardSize())

    @classmethod
    def getInitBoard(cls):
        return utils.getInitBoard()

    def getBoardSize(self):
        board_size = utils.getBoardSize()
        assert board_size[0] >= 16  # need at least this size for data
        return board_size

    def getActionSize(self):
        return len(c.ACTION_LIST)

    def getNextState(self, board, player, action):
        log.debug(f'getNextState({self.stringRepresentation(board)}, {player}, {action}={utils.decodeAction(action)})')
        self.sim.setupBoard(board)

        assert self._thrownStones(utils.getData(board)) < 16
        self.sim.setupAction(player, action)
        self.sim.run()

        next_board = self.sim.getBoard()
        next_player = 0 - player
        log.debug(f'  return board, {next_player}')
        return next_board, next_player

    def getValidMoves(self, board, player):
        self.sim.setupBoard(board)

        data_row = utils.getData(board)

        if self._thrownStones(data_row) >= 16:
            log.error('getValidMoves() requested at game end. Data: %s' % data_row)
            log.error('Board: strRepr' + self.stringRepresentation(board))
            raise utils.GameException('getValidMoves requested after game end.')

        player_turn = utils.getNextPlayer(board, player)
        if player_turn == player:
            return [1] * self.getActionSize()  # all moves are valid

        raise GameException(f'Moves requested for player ({player}) do not match next player ({player_turn})')

    def getGameEnded(self, board, player):
        self.sim.setupBoard(board)
        data_row = utils.getData(board)
        log.debug(f'getGameEnded({self.stringRepresentation(board)})')
        if self._thrownStones(data_row) < 16:
            log.debug('getGameEnded -> 0')
            return 0

        house_radius = utils.dist(feet=6, inches=c.STONE_RADIUS_IN)
        stones = self.sim.getStones()

        # TODO: Optimization - don't compute euclid twice
        near_button = sorted(stones, key=lambda s: utils.euclid(s.body.position, BUTTON_POSITION))
        in_house = list(filter(lambda s: utils.euclid(s.body.position, BUTTON_POSITION) < house_radius, near_button))

        if len(in_house) == 0:
            # Draw is better than being forced to 1
            log.debug('getGameEnded -> draw')
            return 0.00001

        win_color = in_house[0].color
        win_count = 0  # add test
        while len(in_house) > win_count and in_house[win_count].color == win_color:
            win_count += 1

        hammer_won = (win_color == c.P2_COLOR)

        log.debug(f'Win count: {win_count}, color: {win_color}, hammer won: {hammer_won}')
        assert win_count > 0

        if hammer_won:
            if win_count == 1:
                # This is as bad as losing
                return -1
            # 2 or more stones is a great win
            log.debug('getGameEnded -> %s -> 1', win_count)
            return 1

        # a steal is always good
        log.debug('getGameEnded -> %s -> -1', -win_count)
        return -1

    def _thrownStones(self, data_row):
        stones = self.sim.getStones()
        p1_oop = len(np.argwhere(data_row == c.P1_OUT_OF_PLAY))
        p2_oop = len(np.argwhere(data_row == c.P2_OUT_OF_PLAY))
        thrown_stones = len(stones) + p1_oop + p2_oop
        log.debug(f'thrownStones() -> {thrown_stones}')
        assert thrown_stones <= 16
        return thrown_stones

    @staticmethod
    def getCanonicalForm(board, player):
        data_row = utils.getData(board)
        log.debug(f'getCanonicalForm({data_row}, {player})')
        if player == c.P1:
            log.debug(f'getCanonicalForm(board, {player}) -> {data_row}')
            return board

        flip = board * -1

        # Data row remains the same
        flip[-1][0:8] = (board[-1][8:16] * -1)
        flip[-1][8:16] = (board[-1][0:8] * -1)
        log.debug(f'getCanonicalForm(board, {player}) -> {utils.getData(flip)}')
        return flip

    @staticmethod
    def getSymmetries(board, pi):
        # TODO: this can be flipped over y axis
        return [(board, pi)]

    @staticmethod
    def stringRepresentation(board):
        return str(utils.getBoardRepr(board))

    @classmethod
    def boardFromString(cls, string: str):
        # "1: []:2: [[15, 16]]:d: [3, 3, 3, 3, 3, 3, 3, 2, -3, -3, -3, -3, -3, -3, -3, 0]"
        board = cls.getInitBoard()
        log.debug(f'Creating a board of size: {utils.getBoardSize()}')
        data = string.split(':')
        team1 = json.loads(data[1])
        team2 = json.loads(data[3])
        for x, y in team1:
            log.debug(f'Adding "{c.P1}" @ {x, y}')
            board[x, y] = c.P1
        for x, y in team2:
            log.debug(f'Adding "{c.P2}" @ {x, y}')
            board[x, y] = c.P2
        board[-1][0:16] = json.loads(data[5])
        log.debug('Back to string: %s' % cls.stringRepresentation(board))
        assert string == cls.stringRepresentation(board)
        return board

    @classmethod
    def boardFromSchema(cls, data: dict):
        board = cls.getInitBoard()
        log.debug(f'Creating a board of size: {utils.getBoardSize()}')
        team1 = [s for s in data['stones'] if s['color'] == 'red']
        team2 = [s for s in data['stones'] if s['color'] == 'blue']
        game_data = data['game']
        data_row = board[-1]
        data_row[0:game_data['red']] = c.P1_OUT_OF_PLAY
        data_row[8:8+game_data['blue']] = c.P2_OUT_OF_PLAY
        sid = 0
        for s in team1:
            x, y = utils.realToBoard(s['x'] * 12, s['y'] * 12)  # web data is in feet, we're in inches
            log.debug(f'Adding "{c.P1}" @ {x, y}')
            board[x, y] = c.P1
            data_row[sid] = c.EMPTY
            sid += 1

        sid = 8
        for s in team2:
            x, y = utils.realToBoard(s['x'] * 12, s['y'] * 12)  # web data is in feet, we're in inches
            log.debug(f'Adding "{c.P2}" @ {x, y}')
            board[x, y] = c.P2
            data_row[sid] = c.EMPTY
            sid += 1

        str_repr = cls.stringRepresentation(board)
        log.debug('Back to string: %s' % str_repr)
        return board

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
