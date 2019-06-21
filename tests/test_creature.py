import unittest

from combatsim.creature import Creature


class TestCreature(unittest.TestCase):

    def test_ability_modifiers_computed_from_abilties(self):
        creature = Creature(
            strength=4,
            dexterity=5,
            constitution=6,
            intelligence=15,
            wisdom=16,
            charisma=22
        )
        self.assertEqual(creature.str, -3)
        self.assertEqual(creature.dex, -3)
        self.assertEqual(creature.con, -2)
        self.assertEqual(creature.int, 2)
        self.assertEqual(creature.wis, 3)
        self.assertEqual(creature.cha, 6)
