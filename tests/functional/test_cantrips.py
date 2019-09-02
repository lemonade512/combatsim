""" This is a set of functional tests for all cantrips. """

import unittest

import combatsim.cantrips as cantrips
from combatsim.grid import Grid
from combatsim.creature import Creature

from combatsim.tests.mock_dice import MockDice


class TestAcidSplash(unittest.TestCase):

    @MockDice.patch('combatsim.creature', 'combatsim.cantrips')
    def test_acid_splash_against_single_enemy(self):
        # Let's say we have a wizard fighting against a kobold. The wizard only
        # knows acid splash, and the two combatants are 60 feet from each other.
        grid = Grid(60,60)
        wizard = Creature(level=1, max_hp=6)
        kobold = Creature(level=1)

        # The wizard casts acid splash at the kobold, and the kobold passes its
        # dexterity saving throw, thus receiving no damage.
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value > wizard.spell_dc)
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold])
        self.assertEqual(kobold.hp, 6)

        # The wizard casts acid splash at the kobold, and the kobold fails its
        # dexterity save, thus receiving acid damage.
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
        MockDice.set_roll(cantrips.CantripDamage.activate, '1d8', MockDice.value == 1)
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold])
        self.assertEqual(kobold.hp, 6-(1 + wizard.spellcasting))
