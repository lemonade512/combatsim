import unittest

from combatsim.dice import Dice, Modifier
from combatsim.creature import Creature
from combatsim.encounter import Encounter


class TestEncounter(unittest.TestCase):

    def test_initiative_order(self):
        medium = Creature(name="med", initiative=Dice("d1") + Modifier(3))
        fast = Creature(name="fast", initiative=Dice("d1") + Modifier(5))
        slow = Creature(name="slow", initiative=Dice("d1"))
        encounter = Encounter([medium, fast, slow])
        self.assertEqual(encounter.roll_initiative()[0][1].name, fast.name)