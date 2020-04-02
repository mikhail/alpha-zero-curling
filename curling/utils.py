import math

import pymunk

TEAM_1_COLOR = 'red'
TEAM_2_COLOR = 'blue'

STONE_RADIUS_IN = 5.73
STONE_MASS = 2  # units don't matter... 1 'stone" weight.
G_FORCE = 9.81  # In meters
SURFACE_FRICTION = 0.02  # Experimentally picked -- draw weight of 20s

DT = 0.002  # Simulation deltaTime

WEIGHT_FT = {
#    '1': 108,
#    '2': 112,
#    '3': 118,
#    '4': 120,
#    '5': 122,
#    '6': 123,
    '7': 124.5,
#    '8': 126,
#    '9': 127,
#    '10': 129,
#    'backline': 130,
#    'hack': 136,
#    'board': 142,
#    'control': 148,
#    'normal': 154,
#    'peel': 160
}

HANDLES = (1,)  # rotation velocity
BROOMS = (3,) # range(-6,7)

ACTION_LIST = tuple(
    (h,w,b)
        for h in HANDLES
        for w in WEIGHT_FT.keys()
        for b in BROOMS
)

def dist(inches=0, feet=0, meters=0):
    """Returns value in inches"""
    return (feet * 12) + inches + (meters * 39.3701)


def weight_to_dist(w):
    return dist(feet=WEIGHT_FT[w.lower()])

def toFt(x):
    return f'{x/12:3.1f}'


def getPlayerColor(player):
    return sim.TEAM_1_COLOR if player == 1 else sim.TEAM_2_COLOR

class Angle(float):
    def __str__(self):
        if str(self.real) == 'nan':
            return 'x'
        clocks = '🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛'
        i = int(-self.real/6.28*12) % 12
        return clocks[i]

def stone_velocity(body, gravity, damping, dt):
    F_normal = body.mass * dist(meters=G_FORCE)
    F_fr = SURFACE_FRICTION * F_normal
    body.force = body.velocity.normalized() * F_fr * -1

    V_curl = getCurlingVelocity(body) # * dt
    body.velocity -= V_curl

    pymunk.Body.update_velocity(body, gravity, damping, dt)

def calculateVelocityVector(weight: str, broom: int):
    F_normal = STONE_MASS * dist(meters=G_FORCE)
    F_fr = SURFACE_FRICTION * F_normal

    work = weight_to_dist(weight) * F_fr # W = d*F
    vel = math.sqrt(2.0 * work / STONE_MASS)  # W = v^2 * m * 1/2

    x = dist(feet=broom)
    y = weight_to_dist(weight)
    direction = pymunk.Vec2d(x,y).normalized()
    return direction * vel

def addBoundaries(space):
    left = dist(feet=-7)
    right = dist(feet=7)
    # stones are removed when they exit the actual backline.
    backline = dist(feet=130) + 2 * dist(inches=STONE_RADIUS_IN)

    w1, w2, w3 = (
        pymunk.Segment(space.static_body, (left, 0),         (left, backline),  1),
        pymunk.Segment(space.static_body, (left, backline),  (right, backline), 1),
        pymunk.Segment(space.static_body, (right, backline), (right, 0),        1)
    )

    w1.collision_type = 2
    w2.collision_type = 2
    w3.collision_type = 2

    def remove_stone(arbiter, space, data):
        stone = arbiter.shapes[0]
        stone.body.position = (5000, 5000)
        # stone.body.position = (-1,-1)
        stone.body.velocity = 0,0
        #space.remove(stone, stone.body)
        return True

    space.add_collision_handler(1,2).begin = remove_stone

    space.add(w1, w2, w3)

def still_moving(shape):
    vx = abs(shape.body.velocity.x) > 0.01
    vy = abs(shape.body.velocity.y) > 0.01
    return vx or vy


class Stone(pymunk.Circle):

    def __repr__(self):
        return (
            f'<Stone {self.id} {self.color} @ ('
            f'{self.body.position.x:n},{self.body.position.y:n}'
            ')>'
            )

def newStone(color):
    body = pymunk.Body()
    body.velocity_func = stone_velocity
    stone = Stone(body, dist(inches=STONE_RADIUS_IN))
    stone.mass = STONE_MASS
    stone.color = color
    stone.friction = 1.004  # interaction with other objects, not with "ice"
    stone.density = 1
    stone.elasticity = 0.999999

    stone.collision_type = 1
    return stone


def sqGauss(x: float, m = 1, o = 0, em = 1, eo = 0):
    return (x * m + o) * math.exp(-(math.pow(x, 2) * em + eo))


def getCurlingVelocity(body):

    # numbers taken from index.ts but adjusted to work. Unknown discrepancy
    # Adjustments made to curl 6ft on tee-line draw.

    speed = body.velocity.length / 12 / 6  # 12 because ft/inch. 6 - no idea

    # using 008 instead of 005 also don't know why
    curlFromSpeed = sqGauss(speed, 0.008, 0, 0.2, 1.5)

    curl_effect = 1;
    if abs(body.angular_velocity) < 0.01:
        curl_effect = 0;

    direction = 90 if body.angular_velocity < 0 else -90
    curlVector = body.velocity.normalized() * curlFromSpeed * curl_effect
    curlVector.rotate_degrees(direction)

    return curlVector;

def getGameEnded(board, player):
    if board[31] < 1: return 0  # 31 is the Y position of hammer.

    team1 = zip(board[0:8], board[8:16])
    team2 = zip(board[16:24], board[24:32])

    print('failing on purpose')
    raise

def getRoundedBoard(board):
    return [round(v, 2) for v in board]
