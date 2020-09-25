import sys, random
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Joints. Just wait and the L will tip over")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0.0, -900.0)

    lines = add_L(space)
    balls = []
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    ticks_to_next_ball = 10
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        ticks_to_next_ball -= 1
        if ticks_to_next_ball <= 0:
            ticks_to_next_ball = 25
            ball_shape = add_ball(space)
            balls.append(ball_shape)

        screen.fill((255,255,255))

        balls_to_remove = []
        for ball in balls:
            if ball.body.position.y < 150:
                balls_to_remove.append(ball)

        for ball in balls_to_remove:
            space.remove(ball, ball.body)
            balls.remove(ball)

        space.debug_draw(draw_options)

        space.step(1/50.0)

        pygame.display.flip()
        clock.tick(50)

if __name__ == '__main__':
    main()
