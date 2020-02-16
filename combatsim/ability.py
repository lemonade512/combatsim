import math

from combatsim.dice import Modifier

class Ability(Modifier):
    """ Abstraction around abilities. """

    def __init__(self, name, value=None, modifier=None):
        if not value and not modifier:
            raise ValueError(f"No value or modifier specified for {name}")

        if value and modifier:
            raise ValueError(
                f"Cannot specify both modifier and value for {name}"
            )

        if modifier:
            value = Ability._to_value(modifier)
        self.value = value

    def __str__(self):
        return f"Ability({self.value}, ({self.mod}))"

    @property
    def mod(self):
        return math.floor(int(self.value) / 2 - 5)

    @staticmethod
    def _to_value(modifier):
        """ Converts a modifier to a value.

        This will convert to the max possible value for the given modifier.
        So, if the modifier is +3, the value will be 17.
        """
        return 1 + (2 * (modifier + 5))

