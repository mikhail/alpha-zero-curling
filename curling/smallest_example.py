from random import random
import math
import time

import pymunk

def dist(inches=0, feet=0, meters=0):
    return (feet * 12) + inches + (meters * 39.3701)

def toFt(x):
    return f'{x/12:.1f}'

STONE_MASS = 20  # units don't matter... 1 'stone" weight.
STONE_RADIUS = dist(inches=5.73)

DT = 0.0002
SURFACE_FRICTION = 0.02  # draw weight of 20s
G_FORCE = dist(meters=9.81)

def stone_velocity(body, gravity, damping, dt):
    print(f'body.mass = {body.mass}', end="\r")
    F_normal = body.mass * G_FORCE
    F_fr = SURFACE_FRICTION * F_normal
    body.force = body.velocity.normalized() * F_fr * -1

    pymunk.Body.update_velocity(body, gravity, damping, dt)

def calculateVelocityVector(weight: str, broom: int):
    F_normal = STONE_MASS * G_FORCE
    F_fr = SURFACE_FRICTION * F_normal

    work = dist(feet=WEIGHT_DIST[weight]) * F_fr # W = d*F
    vel = math.sqrt(2.0 * work / STONE_MASS)  # W = v^2 * m * 1/2

    x = dist(feet=broom)
    y = dist(feet=WEIGHT_DIST[weight])
    direction = pymunk.Vec2d(x,y).normalized()
    return direction * vel

space = pymunk.Space()
space.gravity = 0,0
space.damping = 1  # No slow down percentage

WEIGHT_DIST = {
    '1': 108,
    '2': 112,
    '3': 118,
    'Biter': 119,
    '4': 120,
    '5': 122,
    '6': 123,
    '7': 124.5,
    '8': 126,
    '9': 127,
    '10': 129,
    'Backline': 130,
    'Hack': 136,
    'Board': 142,
    'Control': 148,
    'Normal': 154,
    'Peel': 160
}



def still_moving(shape):
    vx = abs(shape.body.velocity.x) > 0.01
    vy = abs(shape.body.velocity.y) > 0.01
    return vx or vy


def newStone(color):
    body = pymunk.Body(mass=STONE_MASS)  # , moment=pymunk.inf)
    print(f'body.mass = {body.mass}')
    body.velocity_func = stone_velocity
    stone = pymunk.Circle(body, STONE_RADIUS)
    stone.color = color
    stone.friction = 1.004  # interaction with other objects, not with "ice"
    # stone.density = 1
    #stone.elasticity = 0.999999
    return stone
stone = newStone('blue')
space.add(stone.body, stone)
print(f'stone.body.mass = {stone.body.mass}')
