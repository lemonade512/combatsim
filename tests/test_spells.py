from unittest.mock import Mock, patch
import unittest

from combatsim.creature import Creature
from combatsim.spells import Effect, Heal, Damage


class TestSpellEffects(unittest.TestCase):

    def test_effect_with_single_target(self):
        effect = Effect('target')
        self.assertEqual(effect.get_targets(caster=1, target=2)[0], 2)

    def test_effect_with_self_target(self):
        effect = Effect('self')
        self.assertEqual(effect.get_targets(caster=1, target=2)[0], 1)

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
