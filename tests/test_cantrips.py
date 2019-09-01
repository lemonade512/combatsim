""" This is a set of functional tests for all cantrips. """

import unittest

import combatsim.cantrips as cantrips
from combatsim.grid import Grid
from combatsim.creature import Creature

from combatsim.tests.mock_dice import MockDice

mock_dice = MockDice()


class TestAcidSplash(unittest.TestCase):

    @mock_dice.schedule_cleanup
    def test_acid_splash_against_single_enemy(self):
        # Let's say we have a wizard fighting against a kobold. The wizard only
        # knows acid splash, and the two combatants are 60 feet from each other.
        grid = Grid(60,60)
        wizard = Creature(level=1, max_hp=6)
        kobold = Creature(level=1)

        # Setup mock dice rolls
        mock_dice.patch('combatsim.creature', 'combatsim.cantrips')
        mock_dice.add(kobold.saving_throw, '1d20', mock_dice < wizard.spell_dc)
        mock_dice.add(cantrips.CantripDamage.activate, '1d8', mock_dice == 1)

        # The wizard casts acid splash at the kobold, and the kobold fails its
        # dexterity save, thus receiving acid damage.
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold])
        # TODO: Assert that action was used up
        self.assertEqual(kobold.hp, 6-(1 + wizard.spellcasting))
