import logging
from typing import List

import numpy as np

from curling import constants as c
from curling import utils
from curling.utils import getData

log = logging.getLogger(__name__)


class SimulationException(Exception): pass


class ShooterNotFound(SimulationException): pass


class Timeout(SimulationException): pass


def getNextStoneId(board):
    """Return stone number as it would be in physical game."""
    # FIXME Does not consider out of play stones? or does it...
    data_row = utils.getData(board)
    for i in range(8):
        if data_row[i] == c.P1_NOT_THROWN: return i
        if data_row[i + 8] == c.P2_NOT_THROWN: return i + 8

    log.error('Failure:')
    log.error('Stone locations: %s', utils.getStoneLocations(board))
    log.error('Data row: %s', data_row)
    log.error('Id requested for 9th rock.')
    raise SimulationException()


class Simulation:

    def __init__(self, board_size: (int, int)):
        space = utils.Space(threaded=True)
        space.threads = 12
        space.gravity = 0, 0
        space.damping = 1  # No slow down percentage

        utils.addBoundaries(space)

        self.space = space
        self.boardSize = board_size

        self.resetBoard()
        self.board_before_action = self.getBoard()

    def setupBoard(self, new_board):
        log.debug(f'setupBoard({utils.getBoardRepr(new_board)})')
        self.resetBoard()
        team1 = np.argwhere(new_board == c.P1)
        team2 = np.argwhere(new_board == c.P2)

        for x, y in team1:
            x, y = utils.boardToReal(x, y)
            self.addStone(c.P1_COLOR, x, y)

        for x, y in team2:
            x, y = utils.boardToReal(x, y)
            self.addStone(c.P2_COLOR, x, y)

        self.space.p1_removed_stones = len(np.argwhere(new_board == c.P1_OUT_OF_PLAY))
        self.space.p2_removed_stones = len(np.argwhere(new_board == c.P2_OUT_OF_PLAY))

    def resetBoard(self):
        for stone in self.getStones():
            self.space.remove(stone.body, stone)
        self.space.p1_removed_stones = 0
        self.space.p2_removed_stones = 0

    def addStone(self, color: str, x, y, action=None, stone_id=None):
        stone = utils.newStone(color)
        if stone_id is None:
            stone_id = getNextStoneId(self.getBoard())
        stone.id = stone_id

        stone.body.position = x, y
        stone.updateGuardValue()

        if action is not None:
            handle, weight, broom = utils.decodeAction(action)
            stone.body.angular_velocity = handle
            stone.body.velocity = utils.calculateVelocityVector(weight, broom)
            stone.is_shooter = True

            log.debug(f'Setting HWB: {handle, weight, broom}')
            log.debug(f'Velocity: {stone.body.velocity}')
        else:
            stone.body.angular_velocity = 0
            stone.body.velocity = utils.ZERO_VECTOR

        log.debug("+ %s" % stone)
        self.space.add(stone.body, stone)
        return stone

    def setupAction(self, player, action):
        log.debug(f'setupAction({player}, {action})')
        self.board_before_action = self.getBoard()
        color = utils.getPlayerColor(player)
        self.addStone(color, 0, 0, action)
        self.space.shooter_color = color

    def getShooterStone(self):
        for stone in self.getStones():
            if stone.is_shooter:
                return stone

        log.debug('')
        log.debug(self.getBoard())
        log.debug('')
        raise ShooterNotFound()

    def addShooterAsInvalid(self):
        team = utils.getNextPlayer(self.getBoard())
        if team == c.P1:
            self.space.p1_removed_stones += 1
        else:
            self.space.p2_removed_stones += 1

    def getStones(self) -> List[utils.Stone]:
        return [s for s in self.space.shapes if type(s) == utils.Stone]

    def getBoard(self):
        board = utils.getInitBoard()
        all_stones = list(self.getStones())

        p1_stone_id = self.space.p1_removed_stones
        p2_stone_id = self.space.p2_removed_stones

        board[-1][0:self.space.p1_removed_stones] = [c.P1_OUT_OF_PLAY] * self.space.p1_removed_stones
        board[-1][8:self.space.p2_removed_stones + 8] = [c.P2_OUT_OF_PLAY] * self.space.p2_removed_stones

        for stone in all_stones:
            x, y = utils.realToBoard(stone.body.position.x, stone.body.position.y)
            team_id = stone.getTeamId()
            try:
                board[x][y]
            except IndexError:
                log.warning("Rounding error placed a rock outside of bounds. Removing it")
                if team_id == c.P1:
                    log.warning('Marking p1 stone out of play')
                    board[-1][p1_stone_id] = c.P1_OUT_OF_PLAY
                    p1_stone_id += 1

                if team_id == c.P2:
                    log.warning('Marking p2 stone out of play')
                    board[-1][p2_stone_id + 8] = c.P2_OUT_OF_PLAY
                    p2_stone_id += 1
                continue

            if board[x][y] != c.EMPTY:
                raise SimulationException(f'Space {x, y} occupied by value "{board[x][y]}"')
            board[x][y] = team_id

            if team_id == c.P1:
                board[-1][p1_stone_id] = c.EMPTY
                p1_stone_id += 1

            if team_id == c.P2:
                board[-1][p2_stone_id + 8] = c.EMPTY
                p2_stone_id += 1

        return board

    def run(self, deltaTime=c.DT):
        more_changes = True
        sim_time = 0
        log.debug('run starting...')
        while more_changes:
            self.space.step(deltaTime)

            if self.space.five_rock_rule_violation:
                log.debug('Warning: 5 rock rule violated. Resetting the board!')
                self.setupBoard(self.board_before_action)
                self.addShooterAsInvalid()
                self.space.five_rock_rule_violation = False
                break

            sim_time += deltaTime
            if sim_time > 60:
                log.error('Simulation running for more than 60 seconds.')
                raise Timeout()
            more_changes = any(s.moving() for s in self.space.get_stones())

        log.debug('run() complete with stones: %s and data: %s', self.getStones(), self.getData())

    def getData(self):
        board = self.getBoard()
        return getData(board)
