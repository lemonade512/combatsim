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
    """ Sets up mock values for dice rolls during tests.

    This function is meant to make unit and functional tests easier to write.
    First you must patch the 'Dice' value of any module in which you want to
    roll mock dice. Then, you can attach values to specific methods, classes,
    or functions, and those values will be returned any time there are dice
    rolls in those methods classes or functions. Here is an example::

        @MockDice.patch('combatsim.creature')
        def test_my_class(self):
            kobold = combatsim.creature.Creature()
            MockDice.set(combatsim.creature.Creature, '1d8', [5])
            MockDice.set(kobold.attack, '1d20', [10])

    Whenever dice are rolled in a mocked module, the stack will be inspected
    for three possible cases of mock roles:

        1) Bound method on an objct
        2) Class function
        3) Code file and line number

    If none of those cases match, then the basic Dice class is used for a
    randomized roll.
    """
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
            if 'self' in f.frame.f_locals:
                obj_id = id(f.frame.f_locals['self'])
                # Case: Method
                if (
                    obj_id in MockDice.roll_vals
                    and f.function in MockDice.roll_vals[obj_id]
                    and self.dice in MockDice.roll_vals[obj_id][f.function]
                ):
                    return MockDice.roll_vals[obj_id][f.function][self.dice]

                # Case: Class
                klass = f.frame.f_locals['self'].__class__.__name__
                if (
                    klass in MockDice.roll_vals
                    and self.dice in MockDice.roll_vals[klass]
                ):
                    return MockDice.roll_vals[klass][self.dice]

            # Case: Default
            filename = f.frame.f_code.co_filename
            lineno = f.frame.f_code.co_firstlineno
            if (
                filename in MockDice.roll_vals
                and lineno in MockDice.roll_vals[filename]
                and self.dice in MockDice.roll_vals[filename][lineno]
            ):
                return MockDice.roll_vals[filename][lineno][self.dice]

        # Case: Not found
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
        """ Set roll for the given object.

        This function assumes that you have mocked out the proper modules where
        you want to roll the mock dice.

        Args:
            obj: This can be a function, class, or bound method. When that
                method or class is found in the stack, it will use the given
                value for the given dice role.
            dice: This should be the same as the `dice` argument to the Dice
                class.
            val: The value that should be returned when these mock dice are
                rolled.
        """
        if inspect.ismethod(obj):
            if obj.__name__ not in cls.roll_vals[id(obj.__self__)]:
                cls.roll_vals[id(obj.__self__)][obj.__name__] = dict()
            cls.roll_vals[id(obj.__self__)][obj.__name__][dice] = val
        elif inspect.isclass(obj):
            cls.roll_vals[obj.__name__][dice] = val
        else:
            filename = inspect.getfile(obj)
            lineno = inspect.getsourcelines(obj)[1]
            if lineno not in cls.roll_vals[filename]:
                cls.roll_vals[filename][lineno] = dict()
            cls.roll_vals[filename][lineno][dice] = val
