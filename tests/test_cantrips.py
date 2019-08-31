""" This is a set of functional tests for all cantrips. """

import unittest

from combatsim.cantrips import *
from combatsim.grid import Grid
from combatsim.creature import Creature


class TestAcidSplash(unittest.TestCase):

    def test_acid_splash_against_single_enemy(self):
        # Let's say we have a wizard fighting against a kobold. The wizard only
        # knows acid splash, and the two combatants are 60 feet from each other.
        grid = Grid(60,60)
        wizard = Creature(level=1, max_hp=6)
        kobold = Creature(level=1)

        # The wizard casts acid splash at the kobold, and the kobold fails its
        # dexterity save, thus receiving acid damage.
        wizard.cast(acid_splash, 0, targets=[kobold])
        # TODO: Assert that action was used up
        self.assertEqual(kobold.hp, 5)
