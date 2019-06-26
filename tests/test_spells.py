from unittest.mock import Mock, patch
import unittest

from combatsim.spells import CureWounds


class TestSpellEffects(unittest.TestCase):

    @patch('combatsim.spells.Dice.roll')
    def test_cure_wounds_heals_creature(self, roll):
        roll.return_value = [4]
        creature = Mock()
        creature.spellcasting = 1
        cure_wounds = CureWounds(creature, 1)
        cure_wounds.cast(creature)
        creature.heal.assert_called_with(5)
