import logging
import sys

import coloredlogs
import pygame
import pymunk
from pygame.locals import *

from curling import constants as c, utils
from curling.game import CurlingGame

log = logging.getLogger('')
fmt = '%(asctime)s %(filename).5s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s'
coloredlogs.install(level='INFO', logger=log)
root = logging.getLogger('root')
root.setLevel('INFO')

_DRAW_OFFSET = pymunk.Vec2d(200, -1200)

game = CurlingGame()
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Curling PyGame")
clock = pygame.time.Clock()

space = game.sim.space

log.info('Ready! 🚀 ')


def main():
    action = utils.getAction(-1, '7', -6)
    game.sim.setupAction(1, action)
    log.info("Throwing: %s", utils.decodeAction(action))

    screen.fill((255, 255, 255))
    _draw_house()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        for stone in space.get_stones():
            (x, y) = stone.getXY()
            x += _DRAW_OFFSET.x
            y += _DRAW_OFFSET.y
            pygame.draw.circle(screen, stone.color, (x, y), utils.STONE_RADIUS)

        for _ in range(20):
            space.step(1 / 50.)

        pygame.display.flip()
        clock.tick(50)


def _draw_house():
    pygame.draw.circle(screen, (164, 211, 255),
                       c.BUTTON_POSITION + _DRAW_OFFSET, utils.dist(feet=12))

    pygame.draw.circle(screen, (255, 255, 255),
                       c.BUTTON_POSITION + _DRAW_OFFSET, utils.dist(feet=8))

    pygame.draw.circle(screen, (255, 164, 211),
                       c.BUTTON_POSITION + _DRAW_OFFSET, utils.dist(feet=4))

    pygame.draw.circle(screen, (255, 255, 255),
                       c.BUTTON_POSITION + _DRAW_OFFSET, utils.dist(feet=1))


if __name__ == '__main__':
    main()
