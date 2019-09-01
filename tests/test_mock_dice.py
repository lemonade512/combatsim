""" Verifies that mock dice work. """

import unittest
from unittest.mock import Mock, patch

from tests.mock_dice import MockDice

from combatsim.dice import Dice
import combatsim.creature
import combatsim.encounter

class TestMockDice(unittest.TestCase):

    def setUp(self):
        # TODO (phillip): Figure out how to use configuration or something
        # to make logger just log to console or something.
        self.patcher = patch('combatsim.creature.LOGGER')
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_schedule_cleanup_calls_function_with_args(self):
        func = Mock()
        decorated_func = MockDice.schedule_cleanup(func)
        decorated_func("a", "b")
        func.assert_called_with("a", "b")

    @patch.object(MockDice, 'cleanup')
    def test_schedule_cleanup_runs_cleanup(self, cleanup_func):
        decorated_func = MockDice.schedule_cleanup(Mock())
        decorated_func()
        cleanup_func.assert_called()

    def test_patches_with_mock_dice(self):
        self.assertEqual(combatsim.creature.Dice, Dice)
        MockDice.patch('combatsim.creature')
        self.assertEqual(combatsim.creature.Dice, MockDice)
        MockDice.cleanup()
        self.assertEqual(combatsim.creature.Dice, Dice)

    def test_patchs_multiple_with_mock_dice(self):
        self.assertEqual(combatsim.creature.Dice, Dice)
        self.assertEqual(combatsim.encounter.Dice, Dice)
        MockDice.patch('combatsim.creature', 'combatsim.encounter')
        self.assertEqual(combatsim.creature.Dice, MockDice)
        self.assertEqual(combatsim.encounter.Dice, MockDice)
        MockDice.cleanup()
        self.assertEqual(combatsim.creature.Dice, Dice)
        self.assertEqual(combatsim.encounter.Dice, Dice)

    @MockDice.schedule_cleanup
    def test_mock_dice_fail_tautological_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.patch('combatsim.creature')
        #MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.roll < 0)
        #MockDice.set_roll(kobold.saving_throw, '1d20', -1)
        MockDice.set_roll(kobold, 'saving_throw', -1)
        self.assertFalse(kobold.saving_throw('wisdom', 0))

    @MockDice.schedule_cleanup
    def test_mock_dice_succeed_impossible_save(self):
        kobold = combatsim.creature.Creature()
        MockDice.patch('combatsim.creature')
        #MockDice.set_roll(kobold.saving_throw, '1d20', MockDice.roll > 100)
        #MockDice.set_roll(kobold.saving_throw, '1d20', 101)
        MockDice.set_roll(kobold, 'saving_throw', 101)
        self.assertTrue(kobold.saving_throw('wisdom', 100))
