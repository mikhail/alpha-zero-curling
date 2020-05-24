import json
import logging

import numpy as np
import pylru

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
        self.getValidMovesCache = {}

        self.getNextStateCache: [pylru.lrucache] = []
        for i in range(16):
            self.getNextStateCache.append(pylru.lrucache(2000))

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

        # n.b. This is stones IN PLAY not total thrown stones.
        stone_count = len(self.sim.getStones())  # can be made faster by reading `board` and skip setupBoard
        bpa = (self.stringRepresentation(board), player, action)

        cache_layer = self.getNextStateCache[stone_count]
        if bpa not in cache_layer:

            assert self._thrownStones(utils.getData(board)) < 16
            self.sim.setupAction(player, action)
            self.sim.run()

            next_board = self.sim.getBoard()
            next_player = 0 - player
            result = next_board, next_player
            cache_layer[bpa] = result

        return cache_layer[bpa]

    def getValidMoves(self, board, player):
        # TODO: Skip caching getValidMoves -- we use getNextState anyway!
        board, player = self.getCanonicalForm(board, player), 1

        bp = (self.stringRepresentation(board), player)  # Split this into LRU max 180 each move
        if bp not in self.getValidMovesCache:
            self.sim.setupBoard(board)

            data_row = utils.getData(board)

            if self._thrownStones(data_row) >= 16:
                log.error('getValidMoves() requested at game end. Data: %s' % data_row)
                log.error('Board: strRepr' + self.stringRepresentation(board))
                raise utils.GameException('getValidMoves requested after game end.')

            player_turn = utils.getNextPlayer(board, player)
            if player_turn == player:
                # Do not cause the same state
                # Do not lower your score (or increase their score) ... ok this is really hard and frequently not true
                board_no_data = self.sim.getBoard()[0:-1]
                all_actions = [1] * self.getActionSize()
                for i, act in enumerate(c.ACTION_LIST):
                    newboard, newplayer = self.getNextState(board, player, i)
                    new_board_no_data = newboard[0:-1]
                    if np.array_equal(new_board_no_data, board_no_data):
                        all_actions[i] = 0
                self.getValidMovesCache[bp] = all_actions
            else:
                raise GameException(f'Moves requested for player ({player}) do not match next player ({player_turn})')

        return self.getValidMovesCache[bp]

    def getGameEnded(self, board: np.array, player: int):

        # Convert everything to first-player perspective
        board = self.getCanonicalForm(board, player)
        player_color = c.P1_COLOR  # Because of the canonical form

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

        win_count = 0
        win_color = in_house[0].color
        while len(in_house) > win_count and in_house[win_count].color == win_color:
            win_count += 1

        assert win_count > 0

        we_won = win_color == player_color

        # Ignoring all the fancy logic about hammer or winning by 1 is bad.
        # Too complicated and possibly invalidates the training model
        # because same scenario (one rock in house) has different value for hammer vs not.
        win_value = win_count
        if not we_won:
            win_value *= -1

        log.debug('getGameEnded -> %s', win_value)
        return win_value

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
        size = utils.getBoardSize()
        log.debug(f'Creating a board of size: {size}')
        team1 = [s for s in data['stones'] if s['color'] == 'red']
        team2 = [s for s in data['stones'] if s['color'] == 'blue']
        game_data = data['game']
        data_row = board[-1]
        data_row[0:game_data['red']] = c.P1_OUT_OF_PLAY
        data_row[8:8 + game_data['blue']] = c.P2_OUT_OF_PLAY
        sid = 0
        for s in team1:
            data_row[sid] = c.EMPTY
            sid += 1
            x, y = utils.realToBoard(s['x'] * 12, s['y'] * 12)  # web data is in feet, we're in inches
            if x >= size[0] or y >= size[1]:
                log.warning('Board schema adding stone beyond board size. Ignoring the stone.')
                continue
            log.debug(f'Adding "{c.P1}" @ {x, y}')
            board[x, y] = c.P1

        sid = 8
        for s in team2:
            data_row[sid] = c.EMPTY
            sid += 1
            x, y = utils.realToBoard(s['x'] * 12, s['y'] * 12)  # web data is in feet, we're in inches
            if x >= size[0] or y >= size[1]:
                log.warning('Board schema adding stone beyond board size. Ignoring the stone.')
                continue
            log.debug(f'Adding "{c.P2}" @ {x, y}')
            board[x, y] = c.P2

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
