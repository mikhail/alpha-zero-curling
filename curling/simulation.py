import logging
from typing import List

import numpy as np

from curling import board as board_utils
from curling import constants as c
from curling import utils

log = logging.getLogger(__name__)


class SimulationException(Exception): pass


class ShooterNotFound(SimulationException): pass


class Timeout(SimulationException): pass


def getNextStoneId(board) -> int:
    """Return stone number as it would be in physical game (0-7)."""

    throws = board[c.BOARD_THROWN]

    for i in range(8):
        if throws[i] == c.NOT_THROWN: return i
        if throws[i + 8] == c.NOT_THROWN: return i

    log.error('Failure:')
    log.error('Stone locations: %s', utils.getStoneLocations(board))
    log.error('Throws row: %s', throws)
    log.error('Id requested for 9th rock.')
    raise SimulationException()


def getNextStoneOrderId(board) -> int:
    """Return order id, a value from 0 to 15"""

    throws = board[c.BOARD_THROWN]

    for i in range(8):
        if throws[i] == c.NOT_THROWN: return i
        if throws[i + 8] == c.NOT_THROWN: return i

    log.error('Failure:')
    log.error('Stone locations: %s', utils.getStoneLocations(board))
    log.error('Throws row: %s', throws)
    log.error('Id requested for 9th rock.')
    raise SimulationException()

class Simulation:

    def __init__(self):
        space = utils.Space(threaded=True)
        space.threads = 2
        space.gravity = 0, 0
        space.damping = 1  # No slow down percentage

        utils.addBoundaries(space)

        self.space = space

        self.space.thrown_stones = [c.NOT_THROWN] * 16
        self.space.inplay_stones = [c.IN_PLAY] * 16

        self.resetBoard()
        self.board_before_action = self.getBoard()

    def getBoard(self) -> np.array:

        board = board_utils.getInitBoard()
        board[c.BOARD_THROWN] = self.space.thrown_stones
        board[c.BOARD_IN_PLAY] = self.space.inplay_stones

        log.debug('Populating board from sim.')
        for stone in self.getStones():
            log.debug('Setting board stone %s', stone)
            if stone.color == c.P1_COLOR:
                stone_id = stone.id
            else:
                stone_id = stone.id + 8

            x, y = stone.getXY()
            board[c.BOARD_X][stone_id] = x
            board[c.BOARD_Y][stone_id] = y
            board[c.BOARD_THROWN][stone_id] = c.THROWN
            board[c.BOARD_IN_PLAY][stone_id] = c.IN_PLAY

        return board

    def setupBoard(self, new_board):
        new_board = new_board.copy()
        log.debug(f'setupBoard({board_utils.getBoardRepr(new_board)})')
        self.resetBoard()

        p1_stones = board_utils.stones_for_team(new_board, c.P1)
        for i, (x, y, thrown, in_play) in enumerate(p1_stones):
            if thrown and in_play:
                self.addStone(c.P1_COLOR, x, y, stone_id=i)

        p2_stones = board_utils.stones_for_team(new_board, c.P2)
        for i, (x, y, thrown, in_play) in enumerate(p2_stones):
            if thrown and in_play:
                self.addStone(c.P2_COLOR, x, y, stone_id=i)

        # TODO: Convert all p1/p2_removed_stones to single array. maybe
        self.space.thrown_stones = new_board[c.BOARD_THROWN]
        self.space.inplay_stones = new_board[c.BOARD_IN_PLAY]

    def resetBoard(self):
        for stone in self.getStones():
            self.space.remove(stone.body, stone)
        self.space.thrown_stones = [c.NOT_THROWN] * 16
        self.space.inplay_stones = [c.IN_PLAY] * 16

    def getStones(self) -> List[utils.Stone]:
        # keeping it a list (not an iterator) on purpose
        return [s for s in self.space.shapes if type(s) == utils.Stone]

    def getShooterStone(self):
        for stone in self.getStones():
            if stone.is_shooter:
                return stone

        log.debug('')
        log.debug(self.getBoard())
        log.debug('')
        raise ShooterNotFound()

    def addStone(self, color: str, x, y, action=None, stone_id=None):
        stone = utils.newStone(color)
        board = self.getBoard()
        if stone_id is None:
            stone_id = getNextStoneId(board)
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

        data_position = stone_id if color == c.P1_COLOR else stone_id + 8
        self.space.thrown_stones[data_position] = c.THROWN
        self.space.inplay_stones[data_position] = c.IN_PLAY
        return stone

    def setupAction(self, player, action):
        log.debug(f'setupAction({player}, {action})')
        self.board_before_action = self.getBoard()
        color = utils.getPlayerColor(player)
        self.addStone(color, 0, 0, action)
        self.space.shooter_color = color

    def addShooterAsInvalid(self):
        # Convert removed_stones variable to something else.
        board = self.getBoard()
        team = utils.getNextPlayer(board, c.P1)
        # player = self.getNextPlayer()  # TODO
        if team == c.P1:
            data_position = getNextStoneId(board)
        else:
            data_position = getNextStoneId(board) + 8

        self.space.thrown_stones[data_position] = c.THROWN
        self.space.inplay_stones[data_position] = c.OUT_OF_PLAY

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

        log.debug('run() complete with stones: %s and data: %s', self.getStones(), self.getBoard())
