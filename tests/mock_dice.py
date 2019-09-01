""" Implementation of a test class for dice.

Example:

    class TestCase(unittest.TestCase):
        @test_dice.wrap
        def
"""

from functools import wraps
from unittest.mock import patch


class MockDice:

    def __init__(self):
        self.patches = []

    def wrap(self, test_func):
        """ Decorator for wrapping test functions.

        This decorator will make sure to do patch cleanup once the test
        function has returned.
        """
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            output = test_func(*args, **kwargs)
            self.cleanup()
            return output

    def patch(self, *args):
        """ Patches Dice instances on all modules passed in.

        Args:
            *args: A list of strings that will be passed to the mock patch
                method. For example, you could pass in 'my_module.Dice' to
                patch the Dice class on that module.
        """
        for path in args:
            patcher = patch(path, MockDice)
            self.patches.append(patcher)
            patcher.start()

    def cleanup(self):
        """ Removes all patches that were previously applied. """
        for patch in self.patches:
            patch.stop()
