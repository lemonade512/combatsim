""" This is a set of functional tests for all cantrips. """

import pytest
import unittest

from combatsim.grid import Grid
from combatsim.creature import Monster
from combatsim.rules_error import RulesError

from tests.mock_dice import MockDice


@MockDice.patch('combatsim.creature', 'combatsim.spells')
def test_acid_splash_against_single_enemy(event_log):
    print("HELLO:", repr(event_log))
    import combatsim.cantrips as cantrips  # Must go here so we can mock out dice

    # Let's say we have a wizard fighting against a kobold. The wizard only
    # knows acid splash, and the two combatants are 60 feet from each other.
    grid = Grid(1,80)
    wizard = Monster(level=1, pos=(0,0), grid=grid, spells=[cantrips.acid_splash])
    kobold = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)

    # The wizard casts acid splash at the kobold, and the kobold passes its
    # dexterity saving throw, thus receiving no damage.
    MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value > wizard.spell_dc)
    wizard.cast(cantrips.acid_splash, 0, targets=[kobold])
    assert kobold.hp == 6

    # The wizard casts acid splash at the kobold, and the kobold fails its
    # dexterity save, thus receiving acid damage.
    MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
    MockDice.set_roll(cantrips.CantripDamage.activate, '1d6', MockDice.value == 1)
    wizard.cast(cantrips.acid_splash, 0, targets=[kobold])
    assert kobold.hp == 6-(1 + wizard.spellcasting)

    # The wizard tries to cast acid splash on a location outside the range
    # of the spell, resulting in a rules error.
    kobold.move((0,70))
    with pytest.raises(RulesError):
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold])

@MockDice.patch('combatsim.creature', 'combatsim.spells')
def test_acid_splash_against_two_enemies(event_log):
    import combatsim.cantrips as cantrips  # Must go here so we can mock out dice

    # Let's say we have a wizard fighting against two kobolds. The wizard
    # only knows acid splash, and the two kobolds are 60 feet from the
    # wizard and next to each other.
    grid = Grid(1,60)
    wizard = Monster(level=1, pos=(0,0), grid=grid, spells=[cantrips.acid_splash])
    kobold1 = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)
    kobold2 = Monster(level=1, max_hp=6, pos=(0,58), grid=grid)

    # The wizard casts acid splash at the kobolds, and one kobold passes
    # its saving throw while the other fails.
    MockDice.set_roll(kobold1.saving_throw, '1d20', MockDice.value > wizard.spell_dc)
    MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
    MockDice.set_roll(cantrips.CantripDamage.activate, '1d6', MockDice.value == 1)
    wizard.cast(cantrips.acid_splash, 0, targets=[kobold1, kobold2])
    assert kobold1.hp == 6
    assert kobold2.hp == 6-(1 + wizard.spellcasting)

    # The wizard casts acid splash at the kobolds again, and both kobolds
    # fail their dexterity saves, thus receiving acid damage.
    MockDice.set_roll(kobold1.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
    MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < wizard.spell_dc)
    MockDice.set_roll(cantrips.CantripDamage.activate, '1d6', MockDice.value == 1)
    wizard.cast(cantrips.acid_splash, 0, targets=[kobold1, kobold2])
    assert kobold1.hp == 6-(1 + wizard.spellcasting)
    assert kobold2.hp == 6-(2*(1 + wizard.spellcasting))

    # One of the kobolds moves 11 feet away from the other kobold. The
    # wizard tries to target both kobolds with acid splash resulting in a
    # rules error.
    kobold1.move((0,47))
    with pytest.raises(RulesError):
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold1,kobold2])

@MockDice.patch('combatsim.creature', 'combatsim.spells')
def test_acid_splash_against_three_enemies(event_log):
    import combatsim.cantrips as cantrips  # Must go here so we can mock out dice

    # Let's say we have a wizard fighting against two kobolds. The wizard
    # only knows acid splash, and the two kobolds are 60 feet from the
    # wizard and next to each other.
    grid = Grid(1,60)
    wizard = Monster(level=1, pos=(0,0), grid=grid, spells=[cantrips.acid_splash])
    kobold1 = Monster(level=1, max_hp=6, pos=(0,59), grid=grid)
    kobold2 = Monster(level=1, max_hp=6, pos=(0,58), grid=grid)
    kobold3 = Monster(level=1, max_hp=6, pos=(0,57), grid=grid)

    # A rules error is thrown if the wizard tries to target more than two
    # creatures.
    with pytest.raises(RulesError):
        wizard.cast(cantrips.acid_splash, 0, targets=[kobold1, kobold2, kobold3])

#
## TODO (phillip): Write these tests.
#def TestBladeWard(unittest.TestCase):
#
#    def __init__(self):
#        pass
