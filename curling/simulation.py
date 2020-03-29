import time

import pymunk

import utils

TEAM_1_COLOR = 'red'
TEAM_2_COLOR = 'blue'


class Simulation:

    def setupSpace(self):
        space = pymunk.Space()
        space.gravity = 0,0
        space.damping = 1  # No slow down percentage

        utils.addBoundaries(space)

        self.space = space

    def setupBoard(self, board):
        """Set up stones based on AlphaZero "board" values."""
        self.resetBoard()
        team1 = zip(board[0], board[1])
        team2 = zip(board[2], board[3])
        
        for x,y in team1:
            if y < 1: continue  # not thrown yet
            if y > 140: continue  # (inf) means out of the game
            self.addStone(TEAM_1_COLOR, x, y)

        for x,y in team2:
            if y < 1: continue  # not thrown yet
            if y > 140: continue  # (inf) means out of the game
            self.addStone(TEAM_2_COLOR, x, y)

    def resetBoard(self):
        for shape in self.space.shapes:
            if type(shape) != pymunk.Circle:
                continue
            self.space.remove(shape.body, shape)

    def addStone(self, color, x, y):
        stone = utils.newStone(color)
        stone.body.position = x, y
        self.space.add(stone.body, stone)
    
    def run(self):
        more_changes = True
        last_break = 0
        sim_time = 0
        while more_changes:

            space.step(utils.DT)
            sim_time += utils.DT
            more_changes = False
            if sim_time - last_break > .2:
                print(f"{sim_time:2.0f}s ", end='')
                last_break = sim_time
                for shape in space.shapes:
                    if type(shape) != pymunk.Circle:
                        continue
                    pos = shape.body.position
                    print(
                        f"Stone("
                        f"{shape.color}, "
                        f"x={utils.toFt(pos.x)}ft, y={utils.toFt(pos.y)}ft, "
                        f"v={shape.body.velocity.length:3.0f}, "
                        f"a={utils.Angle(shape.body.angle)})", end=' ')
                print('', end="\r")
            time.sleep(utils.DT/5)

            more_changes = any(utils.still_moving(s) for s in space.shapes)
            if not more_changes:
                print('')
                print('Steady state')
                break
        print()

        for shape in space.shapes:
            if type(shape) != pymunk.Circle:
                continue
            pos = shape.body.position
            print(
                f"Stone("
                f"{shape.color}, "
                f"x={utils.toFt(pos.x)}ft, y={utils.toFt(pos.y)}ft, "
                f"v={shape.body.velocity.length:3.0f}, "
                f"a={utils.Angle(shape.body.angle)})")
