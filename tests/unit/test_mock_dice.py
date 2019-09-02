""" Verifies that mock dice work. """

import unittest
from unittest.mock import Mock, patch

from tests.mock_dice import MockDice, MockRoll

from combatsim.items import Weapon
from combatsim.dice import Dice
import combatsim.creature
import combatsim.items


class MyDummyClass:

    def __init__(self, dice):
        self.dice = dice

    def everything(self):
        return (self.run(), self.throw())

    def run(self):
        return MockDice("1d8").roll()

    def throw(self):
        return self.dice.roll()


class TestMockDice(unittest.TestCase):

    def setUp(self):
        # TODO (phillip): Figure out how to use configuration or something
        # to make logger just log to console or something.
        self.patcher = patch('combatsim.creature.LOGGER')
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_patch_calls_function_with_args(self):
        func = Mock()
        decorated_func = MockDice.patch()(func)
        decorated_func("a", "b")
        func.assert_called_with("a", "b")

    def test_patches_with_mock_dice(self):
        self.assertEqual(combatsim.creature.Dice, Dice)
        @MockDice.patch('combatsim.creature', 'combatsim.items')
        def func():
            self.assertEqual(combatsim.creature.Dice, MockDice)
        func()
        self.assertEqual(combatsim.creature.Dice, Dice)

    def test_patchs_multiple_with_mock_dice(self):
        self.assertEqual(combatsim.creature.Dice, Dice)
        self.assertEqual(combatsim.items.Dice, Dice)
        @MockDice.patch('combatsim.creature', 'combatsim.items')
        def func():
            self.assertEqual(combatsim.creature.Dice, MockDice)
            self.assertEqual(combatsim.items.Dice, MockDice)
        func()
        self.assertEqual(combatsim.creature.Dice, Dice)
        self.assertEqual(combatsim.items.Dice, Dice)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_fail_tautological_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value < 0)
        self.assertFalse(kobold.saving_throw('wisdom', 0))

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_succeed_impossible_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value > 100)
        self.assertTrue(kobold.saving_throw('wisdom', 100))

    @MockDice.patch('combatsim.creature', 'combatsim.items')
    def test_mock_dice_multiple_types(self):
        kobold = combatsim.creature.Monster()
        weapon = Weapon("Longsword", MockDice("1d8"), "slashing", owner=kobold)
        target = Mock()
        target.ac = 1
        MockDice.set_roll(kobold.attack, '1d20', MockDice.value > target.ac)
        MockDice.set_roll(kobold.attack, '1d8', MockDice.value == 10)
        kobold.attack(target, weapon)
        target.take_damage.assert_called_with(10, "slashing")

    @MockDice.patch('combatsim.creature', 'combatsim.items')
    def test_mock_dice_multiple_times(self):
        kobold = combatsim.creature.Monster()
        target = Mock()
        target.ac = 1
        MockDice.set_roll(kobold.attack, '1d20', MockDice.value == 0)
        MockDice.set_roll(kobold.attack, '1d20', MockDice.value > target.ac)
        MockDice.set_roll(kobold.attack, '1d8', MockDice.value == 10)
        kobold.attack(
            target,
            Weapon("Longsword", MockDice("1d8"), "slashing", owner=kobold)
        )
        target.take_damage.assert_called_with(10, "slashing")

    def test_mock_dice_for_multiple_frames_in_stack(self):
        obj = MyDummyClass(MockDice("1d8"))
        MockDice.set_roll(obj.everything, '1d8', MockDice.value == 0)
        MockDice.set_roll(obj.run, '1d8', MockDice.value == 1)
        self.assertEqual(obj.everything(), ([1], [0]))
