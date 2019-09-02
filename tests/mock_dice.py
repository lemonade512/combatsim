""" Implementation of a test class for dice. """

from collections import defaultdict
from functools import wraps
import inspect
import unittest.mock

from combatsim.dice import Dice


class MockRoll:
    """ Helper class to make scripting syntax look cool in functional tests.

    I thought it was neat to make it so that I could specify values for
    functional tests using things like `MockDice.value > target.ac`, so I made
    this class. It doesn't really do anything useful beyond making the tests
    a bit more readable.
    """

    def __lt__(self, other):
        return [other - 1]

    def __gt__(self, other):
        return [other + 1]

    def __eq__(self, other):
        return [other]


class MockDice:
    patches = []
    roll_vals = defaultdict(dict)
    value = MockRoll()

    def __init__(self, dice, modifiers=None):
        self.dice = dice

    def roll(self):
        """ Checks stack for a function with roll value attached.

        This method will traverse up the current frame stack for a code object
        that has had a roll value attached to it with the set_roll method. If
        a value has been attached, that value will be returned. Otherwise, we
        return a randomized value using the default Dice class.
        """
        for f in inspect.stack():
            filename = f.frame.f_code.co_filename
            lineno = f.frame.f_code.co_firstlineno
            if lineno in MockDice.roll_vals[filename]:
                return MockDice.roll_vals[filename][lineno]

        return Dice(self.dice).roll()

    def __add__(self, other):
        return self

    def __mul__(self, other):
        return self

    @classmethod
    def patch(cls, *patches):
        """ Patches Dice instances on all modules passed in.

        Args:
            *patches: A list of strings that will be passed to the mock patch
                method. For example, you could pass in 'my_module.Dice' to
                patch the Dice class on that module.
        """
        def schedule_cleanup(test_func):
            @wraps(test_func)
            def wrapper(*args, **kwargs):
                for path in patches:
                    patcher = unittest.mock.patch(path + '.Dice', MockDice)
                    cls.patches.append(patcher)
                    patcher.start()
                try:
                    output = test_func(*args, **kwargs)
                finally:
                    for patch in cls.patches:
                        patch.stop()
                    cls.patches = []
                    cls.roll_vals = defaultdict(dict)
                return output
            return wrapper
        return schedule_cleanup

    @classmethod
    def set_roll(cls, obj, dice, val):
        filename = inspect.getfile(obj)
        lineno = inspect.getsourcelines(obj)[1]
        cls.roll_vals[filename][lineno] = val
