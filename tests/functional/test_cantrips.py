""" This is a set of functional tests for all cantrips. """

import unittest

import combatsim.cantrips as cantrips
from combatsim.grid import Grid
from combatsim.creature import Monster
from combatsim.rules_error import RulesError

from combatsim.tests.mock_dice import MockDice


class TestAcidSplash(unittest.TestCase):

    @MockDice.patch('combatsim.creature', 'combatsim.cantrips')
    def test_acid_splash_against_single_enemy(self):
        # Let's say we have a wizard fighting against a kobold. The wizard only
        # knows acid splash, and the two combatants are 60 feet from each other.
        grid = Grid(1,80)
        wizard = Monster(level=1, pos=(0,0), grid=grid)
        kobold = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)

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

        # The wizard tries to cast acid splash on a location outside the range
        # of the spell, resulting in a rules error.
        self.assertRaises(RulesError, wizard.cast, cantrip.acid_splash, 0, targets=[(0, 70)])

    @MockDice.patch('combatsim.creature', 'combatsim.cantrips')
    def test_acid_splash_against_two_enemies(self):
        # Let's say we have a wizard fighting against two kobolds. The wizard
        # only knows acid splash, and the two kobolds are 60 feet from the
        # wizard and next to each other.
        grid = Grid(1,60)
        wizard = Monster(level=1, pos=(0,0), grid=grid)
        kobold1 = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)
        kobold2 = Monster(level=1, max_hp=6, pos=(0,58), grid=grid)

        # The wizard casts acid splash at the kobolds, and one kobold passes
        # its saving throw while the other fails.
        MockDice.set_roll(kobold1.saving_throw, '1d20', MockDice.value > wizard.spell_dc)
        MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
        MockDice.set_roll(cantrips.CantripDamage.activate, '1d8', MockDice.value == 1)
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold1, kobold2])
        self.assertEqual(kobold1.hp, 6)
        self.assertEqual(kobold2.hp, 6-(1 + wizard.spellcasting))

        # The wizard casts acid splash at the kobolds again, and both kobolds
        # fail their dexterity saves, thus receiving acid damage. Note that this
        # time the wizard targets the kobolds based on position.
        MockDice.set_roll(kobold1.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
        MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
        MockDice.set_roll(cantrips.CantripDamage.activate, '1d8', MockDice.value == 1)
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold1.pos])
        self.assertEqual(kobold1.hp, 6-(1 + wizard.spellcasting))
        self.assertEqual(kobold2.hp, 6-(2*(1 + wizard.spellcasting)))

        # One of the kobolds moves 10 feet away from the other kobold. The
        # wizard tries to target both kobolds with acid splash resulting in a
        # rules error.
        kobold1.move((0,48))
        self.assertRaises(
            RulesError, wizard.cast, cantrips.acid_splash, 0, targets=[kobold1,kobold2]
        )

    @MockDice.patch('combatsim.creature', 'combatsim.cantrips')
    def test_acid_splash_against_three_enemies(self):
        # Let's say we have a wizard fighting against two kobolds. The wizard
        # only knows acid splash, and the two kobolds are 60 feet from the
        # wizard and next to each other.
        grid = Grid(1,60)
        wizard = Monster(level=1, pos=(0,0), grid=grid)
        kobold1 = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)
        kobold2 = Monster(level=1, max_hp=6, pos=(0,58), grid=grid)
        kobold3 = Monster(level=1, max_hp=6, pos=(0,57), grid=grid)

        # A rules error is thrown if the wizard tries to target more than two
        # creatures.
        self.assertRaises(
            RulesError,
            wizard.cast,
            cantrips.acid_splash,
            0,
            targets=[kobold1, kobold2, kobold3]
        )

        # The wizard casts acid splash at a location within range of all three
        # kobolds. The kobold at the location of the attack is chosen as one of
        # the targets. The second target is either of the other two targets.
        MockDice.set_roll(Monster.saving_throw, '1d20', MockDice.value > wizard.spell_dc)
        MockDice.set_roll(cantrips.CantripDamage.activate, '1d8', MockDice.value == 1)
        wizard.cast(cantrips.acid_splash, 0, targets=(0,58))
        self.assertEqual(kobold2.hp, 6-(1 + wizard.spellcasting))
        self.assertEqual(kobold1.hp + kobold3.hp, 12-(1+wizard.spellcasting))
