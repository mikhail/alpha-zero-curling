from curling import constants as c
from curling import utils


def test_five_rock_rule_first():
    takeout = utils.newStone(c.P1_COLOR)
    space = utils.Space()
    space.get_stones = lambda: []
    space.shooter_color = c.P1_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_second():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 1
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is True


def test_five_rock_rule_fifth():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.get_stones = lambda: ['test'] * 5
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is True


def test_five_rock_rule_sixth():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = True
    space = utils.Space()
    space.thrownStonesCount = lambda: 6
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_not_guard():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = False
    space = utils.Space()
    space.thrownStonesCount = lambda: 1
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_five_rock_rule_not_all_inplay():
    takeout = utils.newStone(c.P1_COLOR)
    takeout.is_guard = False
    space = utils.Space()
    space.thrownStonesCount = lambda: 2
    space.p1_removed_stones = 2
    space.p2_removed_stones = 2
    space.shooter_color = c.P2_COLOR
    assert utils.five_rock_rule(takeout, space) is False


def test_proper_round():
    assert utils.proper_round(0) == 0
    assert utils.proper_round(0.4999999) == 0
    assert utils.proper_round(0.5) == 1
    assert utils.proper_round(0.500000001) == 1
    assert utils.proper_round(0.999999999) == 1
    assert utils.proper_round(1.5) == 2
