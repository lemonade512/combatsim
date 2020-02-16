import pytest
import unittest
from unittest.mock import Mock

from combatsim.items import Armor
from combatsim.creature import Ability, Creature, Monster, RulesError, Character
from combatsim.spells import Spell
from combatsim.dice import Dice, Modifier

TEST_SPELL = Spell("test")


@pytest.fixture
def test_creature():
    return Creature(max_hp=5, spell_slots=[1], spells=[Spell("test")])

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

def test_max_heal_for_creature(test_creature):
    test_creature.hp -= 1
    test_creature.heal(5000)
    assert test_creature.hp == test_creature.max_hp

def test_cast_spell_depletes_spell_slot(test_creature, event_log):
    test_creature.cast(test_creature.spells[0], 1, [])
    assert test_creature.spell_slots[0] == 0

def test_cast_too_many_spells_raises_error(test_creature, event_log):
    test_creature.cast(test_creature.spells[0], 1, [])
    with pytest.raises(RulesError):
        test_creature.cast(test_creature.spells[0], 1, [])

def test_default_ac_is_10_plus_dex_mod():
    creature = Creature(dexterity=15)
    assert creature.ac == 12

def test_ac_can_be_set_directly():
    creature = Creature(ac=14)
    assert creature.ac == 14

def test_ac_set_with_armor_with_no_dex_bonus():
    creature = Creature(armor=Armor("Natural", 12, 0), dexterity=15)
    assert creature.ac == 12

def test_create_creature_from_base():
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
    assert creature.strength == Ability("Strength", 12)
    assert creature.charisma == Ability("Charisma", 14)
    assert creature.name == "Test"

def test_create_creature_from_base_with_customizations():
    base = {
        'name': "Test",
        'strength': 12,
        'dexterity': 15
    }
    creature = Monster.from_base(base, name="New Creature")
    assert creature.name == "New Creature"
    assert creature.strength == Ability("Strength", 12)

def test_creature_max_hp_is_at_least_1():
    creature = Creature(level=1, hd=Dice("1d1"), constitution=2)
    assert creature.max_hp == 1

def test_creature_spell_dc():
    creature = Creature(level=1, spellcasting="wisdom", wisdom=12)
    assert creature.spell_dc == 11

def test_creature_moving_on_grid():
    grid = {(0,0): None, (1,1): None}
    creature = Creature(grid=grid, pos=(0,0))
    assert grid[0, 0] == creature
    creature.move((1,1))
    assert grid[0, 0] == None
    assert grid[1, 1] == creature
    assert creature.x == 1
    assert creature.y == 1

def test_creature_cannot_move_into_non_empty_space():
    grid = {(0,0): None, (1,1): object()}
    creature = Creature(grid=grid, pos=(0,0))
    assert grid[0, 0] == creature
    with pytest.raises(RulesError):
        creature.move((1,1))

def test_distance_to_creature():
    grid = {}
    creature = Creature(grid=grid, pos=(0,0))
    target = Creature(grid=grid, pos=(0,10))
    assert creature.distance_to(target) == 10

def test_player_max_hp_is_at_least_1():
    player = Character(level=1, hd=Dice("1d1"), constitution=2)
    assert player.max_hp == 1
