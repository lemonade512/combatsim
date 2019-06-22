import unittest

from combatsim.dice import Dice, Modifier

# NOTES:
#
#   dice = Dice('d20') + Modifier(1)
#   Advantage = max((dice * 2).roll())
#   Disadvantage = min((dice * 2).roll())
#   Crit Damage = sum((Dice("2d6") * 2).roll()) + Modifier()


class TestDice(unittest.TestCase):

    def test_roll_d1_returns_single_value(self):
        dice = Dice("d1")
        self.assertEqual(dice.roll(), 1)

    def test_roll_multiple_d1s_returns_list(self):
        dice = Dice(["d1", "d1"])
        self.assertEqual(dice.roll(), [1, 1])

    def test_roll_multiple_dice_in_string(self):
        dice = Dice(["5d1"])
        self.assertEqual(dice.roll(), 5)

    def test_roll_with_modifier(self):
        dice = Dice(["1d1"]) + Modifier(1)
        self.assertEqual(dice.roll(), 2)

    def test_multiple_rolls_with_modifiers(self):
        dice = Dice(["2d1", "1d1"]) + Modifier(1)
        self.assertEqual(dice.roll(), [3, 2])

    def test_roll_with_multiple_modifiers(self):
        dice = Dice(["1d1"]) + Modifier(1) + Modifier(2)
        self.assertEqual(dice.roll(), 4)

    def test_add_dynamic_modifiers_to_dice(self):
        modifier = Modifier(1)
        dice = Dice("d1") + modifier
        self.assertEqual(dice.roll(), 2)
        modifier.mod = 2
        self.assertEqual(dice.roll(), 3)

    def test_add_int(self):
        dice = Dice("1d20") + 1
        self.assertEqual(dice, Dice("1d20") + Modifier(1))

    def test_average_d6(self):
        dice = Dice("d6")
        self.assertEqual(dice.average, 3.5)

    def test_average_with_modifiers(self):
        dice = Dice("d6") + Modifier(1)
        self.assertEqual(dice.average, 4.5)

    def test_average_multiple_dice(self):
        dice = Dice(["2d6", "2d8"])
        self.assertEqual(dice.average, 16)

    def test_multiply_dice(self):
        dice = Dice("1d20") * 2
        self.assertEqual(dice, Dice(["1d20", "1d20"]))

    def test_multiply_dice_with_modifiers(self):
        dice = (Dice("1d20") + Modifier(2)) * 2
        self.assertEqual(dice, Dice(["1d20", "1d20"]) + Modifier(2))
