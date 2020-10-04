import logging
import sys
import time

import coloredlogs
import pygame
import pymunk
from pygame.locals import *

from best_action_client import get_best_action
from curling import constants as c, utils
from curling.game import CurlingGame

log = logging.getLogger('')
fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', logger=log)
root = logging.getLogger('root')
root.setLevel('INFO')

_DRAW_OFFSET = pymunk.Vec2d(300, -600)

game = CurlingGame()
pygame.init()
screen = pygame.display.set_mode((600, 1000))
pygame.display.set_caption("Curling PyGame")
clock = pygame.time.Clock()

space = game.sim.space

log.info('Ready! 🚀 ')


def main():
    turns = 16

    tic = 0
    while True:
        screen.fill((255, 255, 255))
        _draw_house()

        tic += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        for stone in space.get_stones():
            (x, y) = stone.getXY()
            x += _DRAW_OFFSET.x
            y += _DRAW_OFFSET.y
            rect = pygame.draw.circle(screen, stone.color, (x, y), utils.STONE_RADIUS)
            pygame.draw.arc(screen, 'black', rect, stone.getAngle(), stone.getAngle() + 1, width=2)

        for _ in range(20):
            space.step(1 / 50.)

        moving = any([s.moving() for s in space.get_stones()])
        if not moving and turns > 0:
            turns -= 1
            _nextTurn(game.sim.getBoard())

        pygame.display.flip()
        clock.tick(50)


def _nextTurn(board):
    try:
        next_player = utils.getNextPlayer(board, c.P1)
    except utils.NobodysTurn:
        log.warning("Game over.")
        return

    color = c.P1_COLOR if next_player == c.P1 else c.P2_COLOR
    best_action = get_best_action(board, player=next_player, use_mcts=True)
    # best_action = 163
    handle, weight, broom = utils.decodeAction(best_action)
    log.info(f"{color} Throwing ({best_action}) {weight} @ {broom}")


    game.sim.setupAction(next_player, best_action)


def _draw_house():
    btn = c.BUTTON_POSITION + _DRAW_OFFSET
    hog = btn - pymunk.Vec2d(0, utils.dist(feet=21))

    pygame.draw.circle(screen, (164, 211, 255), btn, utils.dist(feet=6))
    pygame.draw.circle(screen, (255, 255, 255), btn, utils.dist(feet=4))
    pygame.draw.circle(screen, (255, 164, 211), btn, utils.dist(feet=2))
    pygame.draw.circle(screen, (255, 255, 255), btn, utils.dist(feet=0.5))

    pygame.draw.line(screen, 'black', [(btn.x), 0], [btn.x, 1000])  # Centerline
    pygame.draw.line(screen, 'black', [(btn.x) - 100, btn.y], [(btn.x + 100), btn.y])  # tee line

    pygame.draw.line(screen, 'blue', [(hog.x - 100), hog.y], [(hog.x + 100), hog.y])  # hog line


if __name__ == '__main__':
    main()
