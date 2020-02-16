import pytest
from unittest.mock import Mock, patch
import unittest

from combatsim.creature import Creature
from combatsim.dice import Dice
from combatsim.event import EventLog
from combatsim.spells import (
    Spell, Effect, Heal, Damage, CantripDamage, Sphere, TargetGeometry,
    TargetList, SavingThrow, Effect
)
from combatsim.rules_error import RulesError


def test_iterating_through_targets():
    targets = TargetList()
    targets.add(1)
    targets.add(2)
    assert [t for t in targets] == [1,2]

def test_iterating_through_all_with_tags():
    targets = TargetList()
    targets.add(1, ['enemies'])
    targets.add(2, ['allies'])
    assert [t for t in targets] == [1,2]

def test_iterating_through_tagged_targets():
    targets = TargetList()
    targets.add(1, ['enemies'])
    targets.add(2, ['allies'])
    assert targets['enemies'] == [1]

def test_contains_max_creatures():
    targets = TargetGeometry(max_=2)
    assert targets.contains([(0,0),(1,1)])

def test_contains_more_than_max_creatures_is_false():
    targets = TargetGeometry(max_=2)
    assert not targets.contains([(0,0),(1,1),(2,2)])

@pytest.mark.parametrize("radius,locations,result", [
    (0, [(5,5)], True),
    (0, [(0,0),(5,5)], False),
    (5, [(-5,0),(5,0)], True),
    (5, [(-6,0),(5,0)], False),
    (5, [(7,6),(17,6)], True),
    (5, [(7,6),(17,7)], False)
])
def test_sphere_contains(radius, locations, result):
    assert Sphere(radius=radius).contains(locations) == result

def test_default_initialization():
    spell = Spell("test")
    assert spell.name == "test"
    assert spell.casting_time == "action"
    assert spell.school == "conjuration"
    assert type(spell.targeting) == Sphere
    assert spell.level == 0
    assert spell.range == 0
    assert spell.effects == []

def test_full_initialization():
    spell = Spell(
        "test",
        casting_time="bonus",
        school="evocation",
        level=1,
        range_=5,
        effects=["Test"]
    )
    assert spell.name == "test"
    assert spell.casting_time == "bonus"
    assert spell.school == "evocation"
    assert spell.level == 1
    assert spell.range == 5
    assert spell.effects == ["Test"]

def test_cast_spell_at_lower_level_fails():
    spell = Spell("test", level=2)
    with pytest.raises(RulesError):
        spell.cast(None, 1, [])

def test_cast_spell_out_of_range():
    creature = Mock()
    creature.distance_to.return_value = 6
    spell = Spell("test", range_=5)
    with pytest.raises(RulesError):
        spell.cast(creature, 1, [Mock()])

def test_base_spell_effect_default_initialization():
    effect = Effect()
    assert effect.filters == []
    assert effect.max == None

def test_base_spell_effect_non_default_initialization():
    effect = Effect(max_=5, filters=['a', 'b'])
    assert effect.filters == ['a', 'b']
    assert effect.max == 5

def test_base_spell_effect_filter_none():
    effect = Effect()
    assert effect.filter([1,2,3]) == [1,2,3]

def test_base_spell_effect_filter_enemies():
    effect = Effect(filters=['enemies'])
    assert effect.filter({'all': [1,2], 'enemies': [1]}) == [1]

def test_cantrip_damage_effect_scales_by_level(event_log):
    creature = Mock()
    creature.take_damage.return_value = 1
    creature.spellcasting = 0
    acid = CantripDamage('1d1', 'acid')

    creature.level = 1
    acid.activate(creature, 0, [creature])
    creature.take_damage.assert_called_with(1, 'acid')
    creature.level = 5
    acid.activate(creature, 0, [creature])
    creature.take_damage.assert_called_with(2, 'acid')
    creature.level = 11
    acid.activate(creature, 0, [creature])
    creature.take_damage.assert_called_with(3, 'acid')
    creature.level = 17
    acid.activate(creature, 0, [creature])
    creature.take_damage.assert_called_with(4, 'acid')

def test_saving_throw_defaults_to_all_or_nothing_effect():
    effect = Mock()
    creature = Mock()
    saving_throw = SavingThrow("dexterity", effect)

    creature.saving_throw.return_value = True
    saving_throw.activate(Mock(), 1, [creature])
    effect.activate.asset_not_called()

def test_saving_throw_applies_effect_on_failed_save():
    caster = Mock()
    effect = Mock()
    creature = Mock()
    saving_throw = SavingThrow("dexterity", effect)

    creature.saving_throw.return_value = False
    saving_throw.activate(caster, 1, [creature])
    effect.activate.assert_called_with(caster, 1, [creature])

def test_saving_throw_applies_multiplier_on_save():
    caster = Mock()
    effect = Mock()
    creature = Mock()
    saving_throw = SavingThrow("dexterity", effect, multiplier=0.5)

    creature.saving_throw.return_value = True
    saving_throw.activate(caster, 1, [creature])
    effect.activate.assert_called_with(caster, 1, [creature], multiplier=0.5)
