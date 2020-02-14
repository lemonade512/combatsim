import pytest
import unittest
from unittest.mock import Mock

from combatsim.items import Armor
from combatsim.creature import Ability, Creature, Monster, RulesError, Character
from combatsim.spells import Spell
from combatsim.dice import Dice, Modifier
from combatsim.event import EventLog

TEST_SPELL = Spell("test")

@pytest.mark.parametrize("spell_slots,spell,spell_level", [
    ([], TEST_SPELL, 1),
    ([1], Spell("nonexistant"), 1),
    ([1], TEST_SPELL, 2)
])
def test_cast_spell_raises_error(spell_slots, spell, spell_level):
    with pytest.raises(RulesError):
        creature = Creature(spell_slots=spell_slots, spells=[TEST_SPELL])
        creature.cast(spell, spell_level, [])

@pytest.mark.parametrize("value,modifier", [
    (4,-3),
    (5,-3),
    (6,-2),
    (15,2),
    (22,6)
])
@pytest.mark.parametrize("ability", [
    'strength',
    'dexterity',
    'constitution',
    'intelligence',
    'wisdom',
    'charisma'
])
def test_abilities_computation_of_ability_modifiers(value, modifier, ability):
    creature = Creature(**{ability: value})
    assert getattr(creature, ability).mod == modifier

class TestCreature(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger = EventLog(Mock())

    def test_max_heal_for_creature(self):
        creature = Creature(max_hp=5)
        creature.hp -= 1
        creature.heal(5000)
        self.assertEqual(creature.hp, creature.max_hp)

    def test_cast_spell_depletes_spell_slot(self):
        creature = Creature(spell_slots=[1], spells=[Spell("test")])
        creature.cast(creature.spells[0], 1, [])
        self.assertEqual(creature.spell_slots[0], 0)

    def test_cast_too_many_spells_raises_error(self):
        creature = Creature(spell_slots=[1], spells=[Spell("test")])
        creature.cast(creature.spells[0], 1, [])
        self.assertRaises(RulesError, creature.cast, creature.spells[0], 1, [])

    def test_default_ac_is_10_plus_dex_mod(self):
        creature = Creature(dexterity=15)
        self.assertEqual(creature.ac, 12)

    def test_ac_can_be_set_directly(self):
        creature = Creature(ac=14)
        self.assertEqual(creature.ac, 14)

    def test_ac_set_with_armor_with_no_dex_bonus(self):
        creature = Creature(armor=Armor("Natural", 12, 0), dexterity=15)
        self.assertEqual(creature.ac, 12)

    def test_create_creature_from_base(self):
        base = {
            'name': "Test",
            'strength': 12,
            'dexterity': 12,
            'constitution': 13,
            'wisdom': 12,
            'intelligence': 12,
            'charisma': 14
        }
        creature = Monster.from_base(base)
        self.assertEqual(creature.strength, Ability("Strength", 12))
        self.assertEqual(creature.charisma, Ability("Charisma", 14))
        self.assertEqual(creature.name, "Test")

    def test_create_creature_from_base_with_customizations(self):
        base = {
            'name': "Test",
            'strength': 12,
            'dexterity': 15
        }
        creature = Monster.from_base(base, name="New Creature")
        self.assertEqual(creature.name, "New Creature")
        self.assertEqual(creature.strength, Ability("Strength", 12))

    def test_creature_max_hp_is_at_least_1(self):
        creature = Creature(level=1, hd=Dice("1d1"), constitution=2)
        self.assertEqual(creature.max_hp, 1)

    def test_creature_spell_dc(self):
        creature = Creature(level=1, spellcasting="wisdom", wisdom=12)
        self.assertEqual(creature.spell_dc, 11)

    def test_creature_moving_on_grid(self):
        grid = {(0,0): None, (1,1): None}
        creature = Creature(grid=grid, pos=(0,0))
        self.assertEqual(grid[0, 0], creature)
        creature.move((1,1))
        self.assertEqual(grid[0, 0], None)
        self.assertEqual(grid[1, 1], creature)
        self.assertEqual(creature.x, 1)
        self.assertEqual(creature.y, 1)

    def test_creature_cannot_move_into_non_empty_space(self):
        grid = {(0,0): None, (1,1): object()}
        creature = Creature(grid=grid, pos=(0,0))
        self.assertEqual(grid[0, 0], creature)
        self.assertRaises(RulesError, creature.move, (1,1))

    def test_distance_to_creature(self):
        grid = {}
        creature = Creature(grid=grid, pos=(0,0))
        target = Creature(grid=grid, pos=(0,10))
        self.assertEqual(creature.distance_to(target), 10)


class TestCharacter(unittest.TestCase):

    def test_player_max_hp_is_at_least_1(self):
        player = Character(level=1, hd=Dice("1d1"), constitution=2)
        self.assertEqual(player.max_hp, 1)


class TestAbility(unittest.TestCase):

    def test_add_integers_and_abilities(self):
        ability = Ability("Strength", 15)
        self.assertEqual(5 + ability, 7)
        self.assertEqual(ability + 5, 7)

    def test_sub_integers_and_abilities(self):
        ability = Ability("Dexterity", 15)
        self.assertEqual(5 - ability, 3)
        self.assertEqual(ability - 1, 1)

    def test_set_modifier_fails(self):
        ability = Ability("Constitution", 12)
        with pytest.raises(AttributeError):
            ability.mod = 5

    def test_compare_abilities_with_same_mod(self):
        strength = Ability("Strength", 10)
        dexterity = Ability("Dexterity", 11)
        self.assertTrue(dexterity == strength)
        self.assertTrue(strength == dexterity)

    def test_compare_abilities_with_different_mods(self):
        strength = Ability("Strength", 10)
        dexterity = Ability("Dexterity", 12)
        self.assertTrue(dexterity > strength)
        self.assertTrue(strength < dexterity)

    def test_add_modifier_to_ability_returns_modifier(self):
        strength = Ability("Strength", 12)
        mod = Modifier(2)
        self.assertIsInstance(strength + mod, Modifier)
        self.assertEqual(strength + mod, Modifier(3))
