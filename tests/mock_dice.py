""" Implementation of a test class for dice.

Example:

    class TestCase(unittest.TestCase):
        @test_dice.wrap
        def
"""

from functools import wraps
from unittest.mock import patch


class MockRoll:

    def __init__(self, val):
        self.val = val

    def __call__(self, *args, **kwargs):
        return [self.val]

    def __lt__(self, other):
        return other - 1

    def __gt__(self, other):
        return other + 1


class MockDice:
    patches = []
    roll_val = None

    def __init__(self, dice, modifiers=None):
        self.roll = MockRoll(MockDice.roll_val)

    def __add__(self, other):
        return self

    @classmethod
    def schedule_cleanup(cls, test_func):
        """ Decorator for wrapping test functions.

        This decorator will make sure to do patch cleanup once the test
        function has returned.
        """
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            try:
                output = test_func(*args, **kwargs)
            finally:
                cls.cleanup()
            return output
        return wrapper

    @classmethod
    def patch(cls, *args):
        """ Patches Dice instances on all modules passed in.

        Args:
            *args: A list of strings that will be passed to the mock patch
                method. For example, you could pass in 'my_module.Dice' to
                patch the Dice class on that module.
        """
        for path in args:
            patcher = patch(path + '.Dice', MockDice)
            cls.patches.append(patcher)
            patcher.start()

    @classmethod
    def cleanup(cls):
        """ Removes all patches that were previously applied. """
        for patch in cls.patches:
            patch.stop()
        cls.patches = []

    @classmethod
    def set_roll(cls, obj, attr, val):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                print(func, args)
                temp = MockDice.roll_val
                MockDice.roll_val = val
                output = func(obj, *args, **kwargs)
                MockDice.roll_val = temp
                return output
            return wrapped

        patcher = patch.object(obj, attr, wrapper(obj.__class__.__dict__[attr]))
        patcher.start()
        MockDice.patches.append(patcher)
