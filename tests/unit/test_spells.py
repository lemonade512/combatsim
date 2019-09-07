from unittest.mock import Mock, patch
import unittest

from combatsim.creature import Creature
from combatsim.dice import Dice
from combatsim.spells import Spell, Effect, Heal, Damage, CantripDamage, Sphere
from combatsim.rules_error import RulesError


class TestSphereTargetType(unittest.TestCase):

    def test_radius_0_contains_single_position(self):
        self.assertTrue(Sphere(radius=0).contains((5,5)))


class TestSpell(unittest.TestCase):

    def test_default_initialization(self):
        spell = Spell("test")
        self.assertEqual(spell.name, "test")
        self.assertEqual(spell.casting_time, "action")
        self.assertEqual(spell.school, "conjuration")
        self.assertEqual(spell.level, 0)
        self.assertEqual(spell.range, 0)
        self.assertEqual(spell.effects, [])

    def test_full_initialization(self):
        spell = Spell("test", casting_time="bonus", school="evocation", level=1, range_=5, effects=["Test"])
        self.assertEqual(spell.name, "test")
        self.assertEqual(spell.casting_time, "bonus")
        self.assertEqual(spell.school, "evocation")
        self.assertEqual(spell.level, 1)
        self.assertEqual(spell.range, 5)
        self.assertEqual(spell.effects, ["Test"])


class TestSpellEffects(unittest.TestCase):

    def test_cantrip_damage_effect_scales_by_level(self):
        creature = Mock()
        creature.spellcasting = 0
        acid = CantripDamage('self', Dice('1d1'), None, 'acid')

        creature.level = 1
        acid.activate(creature, creature, 0)
        creature.take_damage.assert_called_with(1, 'acid')
        creature.level = 5
        acid.activate(creature, creature, 0)
        creature.take_damage.assert_called_with(2, 'acid')
        creature.level = 11
        acid.activate(creature, creature, 0)
        creature.take_damage.assert_called_with(3, 'acid')
        creature.level = 17
        acid.activate(creature, creature, 0)
        creature.take_damage.assert_called_with(4, 'acid')
