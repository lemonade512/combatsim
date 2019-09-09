from unittest.mock import Mock, patch
import unittest

from combatsim.creature import Creature
from combatsim.dice import Dice
from combatsim.spells import (
    Spell, Effect, Heal, Damage, CantripDamage, Sphere, TargetGeometry,
    TargetList, SavingThrow, Effect
)
from combatsim.rules_error import RulesError


class TestTargetList(unittest.TestCase):

    def test_iterating_through_targets(self):
        targets = TargetList()
        targets.add(1)
        targets.add(2)
        self.assertEqual([t for t in targets], [1,2])

    def test_iterating_through_all_with_tags(self):
        targets = TargetList()
        targets.add(1, ['enemies'])
        targets.add(2, ['allies'])
        self.assertEqual([t for t in targets], [1,2])

    def test_iterating_through_tagged_targets(self):
        targets = TargetList()
        targets.add(1, ['enemies'])
        targets.add(2, ['allies'])
        self.assertEqual(targets['enemies'], [1])


class TestTargetGeometry(unittest.TestCase):

    def test_contains_max_creatures(self):
        targets = TargetGeometry(max_=2)
        self.assertTrue(targets.contains([(0,0),(1,1)]))

    def test_contains_more_than_max_creatures_is_false(self):
        targets = TargetGeometry(max_=2)
        self.assertFalse(targets.contains([(0,0),(1,1),(2,2)]))


class TestSphereTargetGeometry(unittest.TestCase):

    def test_radius_0_contains_single_position(self):
        self.assertTrue(Sphere(radius=0).contains([(5,5)]))

    def test_radius_0_does_not_contain_two_positions(self):
        self.assertFalse(Sphere(radius=0).contains([(0,0),(5,5)]))

    def test_radius_5_contains_two_positions(self):
        self.assertTrue(Sphere(radius=5).contains([(-5,0),(5,0)]))

    def test_radius_5_does_not_contain_two_positions(self):
        self.assertFalse(Sphere(radius=5).contains([(-6,0),(5,0)]))

    def test_radius_5_contains_two_positions_not_origin(self):
        self.assertTrue(Sphere(radius=5).contains([(7,6),(17,6)]))

    def test_radius_5_does_not_contain_two_positions_not_origin(self):
        self.assertFalse(Sphere(radius=5).contains([(7,6),(17,7)]))


class TestSpell(unittest.TestCase):

    def test_default_initialization(self):
        spell = Spell("test")
        self.assertEqual(spell.name, "test")
        self.assertEqual(spell.casting_time, "action")
        self.assertEqual(spell.school, "conjuration")
        self.assertEqual(type(spell.targeting), Sphere)
        self.assertEqual(spell.level, 0)
        self.assertEqual(spell.range, 0)
        self.assertEqual(spell.effects, [])

    def test_full_initialization(self):
        spell = Spell(
            "test",
            casting_time="bonus",
            school="evocation",
            level=1,
            range_=5,
            effects=["Test"]
        )
        self.assertEqual(spell.name, "test")
        self.assertEqual(spell.casting_time, "bonus")
        self.assertEqual(spell.school, "evocation")
        self.assertEqual(spell.level, 1)
        self.assertEqual(spell.range, 5)
        self.assertEqual(spell.effects, ["Test"])

    def test_cast_spell_at_lower_level_fails(self):
        spell = Spell("test", level=2)
        self.assertRaises(RulesError, spell.cast, None, 1, [])

    def test_cast_spell_out_of_range(self):
        creature = Mock()
        creature.distance_to.return_value = 6
        spell = Spell("test", range_=5)
        self.assertRaises(RulesError, spell.cast, creature, 1, [Mock()])


class TestSpellEffects(unittest.TestCase):

    def test_base_spell_effect_default_initialization(self):
        effect = Effect()
        self.assertEqual(effect.filters, [])
        self.assertEqual(effect.max, None)

    def test_base_spell_effect_non_default_initialization(self):
        effect = Effect(max_=5, filters=['a', 'b'])
        self.assertEqual(effect.filters, ['a', 'b'])
        self.assertEqual(effect.max, 5)

    def test_base_spell_effect_filter_none(self):
        effect = Effect()
        self.assertEqual(effect.filter([1,2,3]), [1,2,3])

    def test_base_spell_effect_filter_enemies(self):
        effect = Effect(filters=['enemies'])
        self.assertEqual(effect.filter({'all': [1,2], 'enemies': [1]}), [1])

    def test_cantrip_damage_effect_scales_by_level(self):
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

    def test_saving_throw_defaults_to_all_or_nothing_effect(self):
        effect = Mock()
        creature = Mock()
        saving_throw = SavingThrow("dexterity", effect)

        creature.saving_throw.return_value = True
        saving_throw.activate(Mock(), 1, [creature])
        effect.activate.asset_not_called()

    def test_saving_throw_applies_effect_on_failed_save(self):
        caster = Mock()
        effect = Mock()
        creature = Mock()
        saving_throw = SavingThrow("dexterity", effect)

        creature.saving_throw.return_value = False
        saving_throw.activate(caster, 1, [creature])
        effect.activate.assert_called_with(caster, 1, [creature])

    def test_saving_throw_applies_multiplier_on_save(self):
        caster = Mock()
        effect = Mock()
        creature = Mock()
        saving_throw = SavingThrow("dexterity", effect, multiplier=0.5)

        creature.saving_throw.return_value = True
        saving_throw.activate(caster, 1, [creature])
        effect.activate.assert_called_with(caster, 1, [creature], multiplier=0.5)
