from unittest.mock import Mock, patch
import unittest

from combatsim.creature import Creature
from combatsim.dice import Dice
from combatsim.spells import Effect, Heal, Damage, CantripDamage
from combatsim.rules_error import RulesError


# TODO (phillip): Separate these test cases out. There can be a test case for
# the base spell effects class, then a separate test case for each spell effect.
class TestSpellEffects(unittest.TestCase):

    def test_effect_with_single_target(self):
        effect = Effect('target')
        self.assertEqual(effect.get_targets(caster=1, target=2)[0], 2)

    def test_effect_with_self_target(self):
        effect = Effect('self')
        self.assertEqual(effect.get_targets(caster=1, target=2)[0], 1)

    def test_effect_with_multiple_targets(self):
        effect = Effect('targets')
        self.assertEqual(effect.get_targets(caster=1, targets=[2,3]), [2,3])

    def test_effect_with_min_targets_raises_rules_error(self):
        effect = Effect('targets', props={'min_targets': 2})
        self.assertRaises(RulesError, effect.get_targets, caster=1, targets=[2])

    def test_effect_with_max_targets_raises_rules_error(self):
        effect = Effect('targets', props={'max_targets': 2})
        self.assertRaises(RulesError, effect.get_targets, caster=1, targets=[2,3,4])

    @patch("combatsim.dice.random.randint")
    def test_heal_effect_at_level_1(self, randint):
        randint.return_value = 1
        creature = Creature(max_hp=5, hp=1)
        heal = Heal('self')
        heal.activate(creature, 1)
        self.assertEqual(creature.hp, 2)

    @patch("combatsim.dice.random.randint")
    def test_heal_effect_at_level_3(self, randint):
        randint.return_value = 1
        creature = Creature(max_hp=5, hp=1)
        heal = Heal('self')
        heal.activate(creature, 3)
        self.assertEqual(creature.hp, 4)

    @patch("combatsim.dice.random.randint")
    def test_damage_effect_does_acid_damage(self, randint):
        randint.return_value = 2
        creature = Mock()
        creature.spellcasting = 0
        acid = Damage('self', None, 'acid')
        acid.activate(creature, 1)
        creature.take_damage.assert_called_with(2, 'acid')

    def test_cantrip_damage_effect_scales_by_level(self):
        creature = Mock()
        creature.spellcasting = 0
        acid = CantripDamage('self', Dice('1d1'), None, 'acid')

        creature.level = 1
        acid.activate(creature, 0)
        creature.take_damage.assert_called_with(1, 'acid')
        creature.level = 5
        acid.activate(creature, 0)
        creature.take_damage.assert_called_with(2, 'acid')
        creature.level = 11
        acid.activate(creature, 0)
        creature.take_damage.assert_called_with(3, 'acid')
        creature.level = 17
        acid.activate(creature, 0)
        creature.take_damage.assert_called_with(4, 'acid')

    def test_piped_effect(self):
        # TODO
        pass

    #@patch('combatsim.spells.Dice.roll')
    #def test_cure_wounds_heals_creature(self, roll):
    #    roll.return_value = [4]
    #    creature = Mock()
    #    creature.spellcasting = 1
    #    cure_wounds = CureWounds(creature, 1)
    #    cure_wounds.cast(creature)
    #    creature.heal.assert_called_with(5)
