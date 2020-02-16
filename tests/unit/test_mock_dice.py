""" Verifies that mock dice work. """

import pytest
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


@pytest.mark.usefixtures("event_log")
class TestMockDice:

    def test_patch_calls_function_with_args(self):
        func = Mock()
        decorated_func = MockDice.patch()(func)
        decorated_func("a", "b")
        func.assert_called_with("a", "b")

    def test_patches_with_mock_dice(self):
        assert combatsim.creature.Dice == Dice
        @MockDice.patch('combatsim.creature', 'combatsim.items')
        def func():
            assert combatsim.creature.Dice == MockDice
        func()
        assert combatsim.creature.Dice == Dice

    def test_patches_multiple_with_mock_dice(self):
        assert combatsim.creature.Dice == Dice
        assert combatsim.items.Dice == Dice
        @MockDice.patch('combatsim.creature', 'combatsim.items')
        def func():
            assert combatsim.creature.Dice == MockDice
            assert combatsim.items.Dice == MockDice
        func()
        assert combatsim.creature.Dice == Dice
        assert combatsim.items.Dice == Dice

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_fail_tautological_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value < 0)
        assert not kobold.saving_throw('wisdom', 0)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_succeed_impossible_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.value > 100)
        assert kobold.saving_throw('wisdom', 100)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_multiple_creatures(self):
        kobold1 = combatsim.creature.Creature()
        kobold2 = combatsim.creature.Creature()
        MockDice.set_roll(kobold1.saving_throw, '1d20', MockDice.value > 100)
        MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < 0)
        assert kobold1.saving_throw('wisdom', 100)
        assert not kobold2.saving_throw('wisdom', 0)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_on_class(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(combatsim.creature.Creature, '1d20', MockDice.value > 100)
        assert kobold.saving_throw('wisdom', 100)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_on_class_function(self):
        kobold = combatsim.creature.Creature()
        MockDice.set_roll(combatsim.creature.Creature.saving_throw, '1d20', MockDice.value > 100)
        assert kobold.saving_throw('wisdom', 100)

    @MockDice.patch('combatsim.creature')
    def test_mock_dice_object_overrides_class(self):
        kobold1 = combatsim.creature.Creature()
        kobold2 = combatsim.creature.Creature()
        MockDice.set_roll(combatsim.creature.Creature.saving_throw, '1d20', MockDice.value > 100)
        MockDice.set_roll(kobold2.saving_throw, '1d20', MockDice.value < 0)
        assert kobold1.saving_throw('wisdom', 100)
        assert not kobold2.saving_throw('wisdom', 0)

    @MockDice.patch('combatsim.creature', 'combatsim.items')
    def test_mock_dice_multiple_types(self):
        kobold = combatsim.creature.Monster()
        weapon = Weapon("Longsword", MockDice("1d8"), "slashing", owner=kobold)
        target = Mock()
        target.ac = 15
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
        assert obj.everything() == ([1], [0])
