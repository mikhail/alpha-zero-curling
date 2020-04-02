import sys
import time

import numpy as np
import pymunk

from . import utils

TEAM_1_COLOR = 'red'
TEAM_2_COLOR = 'blue'

class SimulationException(Exception): pass

def getPlayerColor(player):
    return TEAM_1_COLOR if player == 1 else TEAM_2_COLOR

def getNextStoneId(board):
    """Return stone number as it would be in physical game."""

    for i in range(8):
        if board[i + 8] < 1: return i
        if board[i + 24] < 1: return i

    raise SimulationException('Id requested for 9th rock')

def decodeAction(action):
    assert action >= 0
    return utils.ACTION_LIST[action]



class Simulation:

    def __init__(self, boardSize=40):
        space = pymunk.Space()
        space.gravity = 0,0
        space.damping = 1  # No slow down percentage

        utils.addBoundaries(space)

        self.space = space
        self.debug = False
        self.boardSize = boardSize

        self.resetBoard()

    def print(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def setupBoard(self, board):
        self.resetBoard()
        team1 = zip(board[0:8], board[8:16])
        team2 = zip(board[16:24], board[24:32])
        
        sid = -1
        for x,y in team1:
            sid += 1
            if y < 1: continue  # not thrown yet
            s = self.addStone(TEAM_1_COLOR, x, y)
            s.id = sid

        sid = -1
        for x,y in team2:
            sid += 1
            if y < 1: continue  # not thrown yet
            s = self.addStone(TEAM_2_COLOR, x, y)
            s.id = sid

    def resetBoard(self):
        #self.board = np.zeros(self.boardSize);
        for stone in self.getStones():
            if stone.body:
                self.space.remove(stone.body, stone)
            else:
                self.space.remove(stone)

    def addStone(self, color, x, y, action=None, stone_id=None):
        stone = utils.newStone(color)
        if stone_id is None:
            stone_id = getNextStoneId( self.getBoard() )
        stone.id = stone_id
 
        if y > 2000:  # off the board
            x = pymunk.inf
            y = pymunk.inf

        stone.body.position = x, y

        if action is not None:
            handle, weight, broom = decodeAction(action)
            self.print(f'Setting HWB: {handle, weight, broom}')
            stone.body.angular_velocity = handle
            stone.body.velocity = utils.calculateVelocityVector(weight, broom)
            self.print(f'Velocity: {stone.body.velocity}')
        self.print('Adding stone')
        self.space.add(stone.body, stone)
        return stone

    def setupAction(self, player, action):
        color = getPlayerColor(player)
        s = self.addStone(color, 0, 0, action)
        s.id = getNextStoneId(self.getBoard())

    def getStones(self):
        return (s for s in self.space.shapes if type(s) == utils.Stone)

    def getBoard(self):
        board = np.zeros(self.boardSize);
        all_stones = list(self.getStones())

        print('beginning loop')
        for stone in all_stones:
            print('Adding stone obj id ', id(stone))
            if stone.color == TEAM_1_COLOR:
                print('Stone.id = %s. obj id = %s ' %( stone.id, id(stone)))
                x_id = stone.id
                y_id = x_id + 8
            else:
                x_id = stone.id + 16
                y_id = x_id + 8

            board[x_id] = stone.body.position.x if stone.body else 5000
            board[y_id] = stone.body.position.y if stone.body else 5000

        return board
    
    def run(self, deltaTime=utils.DT): 
        # print(''.join(['🥌'] * len(list(self.getStones()))))
        print(utils.getRoundedBoard( self.getBoard() ) )
        more_changes = True
        last_break = 0
        sim_time = 0
        while more_changes:
            self.space.step(deltaTime)
            sim_time += deltaTime
            if sim_time > 60:
                return
            more_changes = False
            if sim_time - last_break > .2:
                self.print(f"{sim_time:2.0f}s ", end='')
                last_break = sim_time
                for stone in self.getStones():
                    #pos = stone.body.position
                    self.print(
                        f"Stone("
                        f"{stone.color}, "
                        #f"x={utils.toFt(pos.x)}ft, y={utils.toFt(pos.y)}ft, "
                        # f"v={stone.body.velocity.length:3.0f}, "
                        # f"a={utils.Angle(stone.body.angle)})"
                        , end=' ')
                self.print('', end="\r")
            if self.debug:
                time.sleep(deltaTime/5)

            more_changes = any(utils.still_moving(s) for s in self.space.shapes)
            if not more_changes:
                self.print('')
                self.print('Steady state')
                break
        self.print()

        for stone in self.getStones():
            #pos = stone.body.position
            self.print(
                f"Stone("
                f"{stone.color}, "
                # f"x={utils.toFt(pos.x)}ft, y={utils.toFt(pos.y)}ft, "
                # f"v={stone.body.velocity.length:3.0f}, "
                # f"a={utils.Angle(stone.body.angle)})"
                )
