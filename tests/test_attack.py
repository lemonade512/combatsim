import unittest
from unittest.mock import patch

from combatsim.attacks import Attack
from combatsim.creature import Monster
from combatsim.dice import Dice

dummy_monster = Monster()


class TestAttack(unittest.TestCase):

    @patch("combatsim.dice.random.randint")
    def test_attack_with_advantage_returns_max(self, randint):
        randint.side_effect = [1, 20]
        attack = Attack("test", None, None, owner=dummy_monster)
        self.assertEqual(attack.attack_roll(advantage=True)[0], 20)

    @patch("combatsim.dice.random.randint")
    def test_attack_with_disadvantage_returns_min(self, randint):
        randint.side_effect = [1, 20]
        attack = Attack("test", None, None, owner=dummy_monster)
        self.assertEqual(attack.attack_roll(disadvantage=True)[0], 1)

    @patch("combatsim.dice.random.randint")
    def test_attack_returns_single_value(self, randint):
        randint.side_effect = [5, 15]
        attack = Attack("test", None, None, owner=dummy_monster)
        self.assertEqual(attack.attack_roll()[0], 5)

    @patch("combatsim.dice.random.randint")
    def test_attack_with_finess_uses_max_of_strength_and_dex(self, randint):
        randint.return_value = 5
        strong_monster = Monster(strength=18)
        attack = Attack("test", None, None, owner=strong_monster, properties=["finesse"])
        self.assertEqual(attack.attack_roll()[0], 9)
        fast_monster = Monster(dexterity=18)
        attack.owner = fast_monster
        self.assertEqual(attack.attack_roll()[0], 9)

    @patch("combatsim.dice.random.randint")
    def test_melee_attack_uses_strength(self, randint):
        randint.return_value = 1
        strong_monster = Monster(strength=18)
        attack = Attack("test", None, None, melee=True, owner=strong_monster)
        self.assertEqual(attack.attack_roll()[0], 5)

    @patch("combatsim.dice.random.randint")
    def test_ranged_attack_uses_dexterity(self, randint):
        randint.return_value = 1
        fast_monster = Monster(dexterity=18)
        attack = Attack("test", None, None, melee=False, owner=fast_monster)
        self.assertEqual(attack.attack_roll()[0], 5)

    @patch("combatsim.dice.random.randint")
    def test_advantage_disadvantage_cancel_out(self, randint):
        randint.side_effect = [1, 20]
        attack = Attack("test", None, None, owner=dummy_monster)
        self.assertEqual(attack.attack_roll(advantage=True, disadvantage=True)[0], 1)
        self.assertEqual(attack.attack_roll(advantage=True, disadvantage=True)[0], 20)

    @patch("combatsim.dice.random.randint")
    def test_crit_is_returned_on_nat_20(self, randint):
        randint.return_value = 20
        attack = Attack("test", None, None, owner=dummy_monster)
        self.assertTrue(attack.attack_roll()[1])

    @patch("combatsim.dice.random.randint")
    def test_crit_not_returned_on_modified_20(self, randint):
        randint.return_value = 19
        monster = Monster(strength=12)
        attack = Attack("test", None, None, owner=monster)
        roll, crit = attack.attack_roll()
        self.assertEqual(roll, 20)
        self.assertFalse(crit)
