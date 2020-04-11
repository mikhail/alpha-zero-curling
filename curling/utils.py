import math

import pymunk

class FiveRockViolation(Exception):
    pass

TEAM_1_COLOR = 'red'
TEAM_2_COLOR = 'blue'

STONE_RADIUS_IN = 5.73
STONE_MASS = 2  # units don't matter... 1 'stone" weight.
G_FORCE = 9.81  # In meters
SURFACE_FRICTION = 0.02  # Experimentally picked -- draw weight of 20s

DT = 0.002  # Simulation deltaTime

INVALID_VALUE = 5000

WEIGHT_FT = {
#    '1': 108,
#    '2': 112,
    '3': 118,
    '4': 120,
    '5': 122,
    '6': 123,
    '7': 124.5,
     '8': 126,
#    '9': 127,
#    '10': 129,
#    'backline': 130,
#    'hack': 136,
#    'board': 142,
    'control': 148,
#    'normal': 154,
#    'peel': 160
}

HANDLES = (1, -1)  # rotation velocity
BROOMS = range(-6,7)

ACTION_LIST = tuple(
    (h,w,b)
        for h in HANDLES
        for w in WEIGHT_FT.keys()
        for b in BROOMS
)


class Space(pymunk.Space):

    def get_stones(self):
        return [s for s in self.shapes if type(s) == Stone]

    def get_shooter(self):
        shooters = [s for s in self.get_stones() if s.is_shooter]

        assert len(shooters) == 1

        return shooters[0]

def getPlayerColor(player):
    return TEAM_1_COLOR if player == 1 else TEAM_2_COLOR


def decodeAction(action):
    assert action >= 0
    return ACTION_LIST[action]


def dist(inches=0, feet=0, meters=0):
    """Returns value in inches"""
    return (feet * 12) + inches + (meters * 39.3701)


def weight_to_dist(w):
    return dist(feet=WEIGHT_FT[w.lower()])

def toFt(x):
    return f'{x/12:3.1f}'


def getPlayerColor(player):
    return TEAM_1_COLOR if player == 1 else TEAM_2_COLOR

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

        if five_rock_rule(stone, space):
            # mark the shooter as a violator? but we don't have the shooter here
            # mark THIS stone as "taken out during violation"
            stone.removed_by_violation = True

        stone.body.position = (INVALID_VALUE, INVALID_VALUE)
        stone.body.velocity = 0,0
        return True

    space.add_collision_handler(1,2).begin = remove_stone

    space.add(w1, w2, w3)

def still_moving(shape):
    vx = abs(shape.body.velocity.x) > 0.01
    vy = abs(shape.body.velocity.y) > 0.01
    return vx or vy


class Stone(pymunk.Circle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set to true if stone created in the guard zone. Used for 5-rock rule
        self.is_guard = False

        # Indicates that this is the stone that will be thrown.
        self.is_shooter = False

        # Set to true to indicate to the step() caller to undo the board setup
        self.removed_by_violation = False



    def __repr__(self):
        return (
            f'<Stone {self.id} {self.color} @ ('
            f'{self.body.position.x:n},{self.body.position.y:n}'
            ')>'
            )

    def remove_from_game(self):
        self.body.position = (INVALID_VALUE, INVALID_VALUE)
        self.body.velocity = 0,0

    def moving(self):
        vx = abs(self.body.velocity.x) > 0.01
        vy = abs(self.body.velocity.y) > 0.01
        return vx or vy

    def updateGuardValue(self):
        radius = dist(inches=STONE_RADIUS_IN)
        hog_line = radius + dist(feet=6 + 6 + 21 + 72)
        tee_line = hog_line + dist(feet=21)
        from_pin = euclid(self.body.position, pymunk.Vec2d(0, tee_line))

        y = self.body.position.y

        before_tee = hog_line < y < tee_line
        not_in_house = from_pin > dist(feet=6) + radius

        self.is_guard = before_tee and not_in_house


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

def getRoundedBoard(board):
    return [round(v, 2) for v in board]

def euclid(v1, v2):
    return math.sqrt( ((v1.x-v2.x)**2)+((v1.y-v2.y)**2) )

def five_rock_rule(stone, space):
    shooter = space.get_shooter()

    if len(space.get_stones()) > 5:
        return False

    if shooter.color == stone.color:
        return False

    if stone.is_guard == False:
        return False

    return True

