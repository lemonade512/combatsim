""" Defines helper classes for rolling dice. """

import random


class Modifier:

    def __init__(self, modifier):
        self.mod = modifier

    def __add__(self, other):
        if isinstance(other, int):
            return other + self.mod

        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, int):
            return self.mod - other

        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, int):
            return other - self.mod

        return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Modifier):
            return NotImplemented

        return self.mod == other.mod


class Dice:

    def __init__(self, dice, modifiers=None):
        if not isinstance(dice,list):
            dice = [dice]

        # Initialize dice, parsing strings as necessary
        self.dice = []
        for die in dice:
            if isinstance(die, str):
                self.dice.append(Dice._parse(die))
            else:
                self.dice.append(die)

        if not modifiers:
            modifiers = []
        self.modifiers = modifiers

    def __eq__(self, other):
        if not isinstance(other, Dice):
            return NotImplemented

        return self.dice == other.dice and self.modifiers == other.modifiers

    def __add__(self, other):
        if isinstance(other, int):
            return Dice(self.dice, self.modifiers + [Modifier(other)])

        if isinstance(other, Modifier):
            return Dice(self.dice, self.modifiers + [other])

        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return Dice(self.dice * other, self.modifiers)

        return NotImplemented

    def __str__(self):
        total_mod = sum(self.modifiers)
        out = [f"{x}d{y} + {total_mod}" for x,y in self.dice]
        return f"Dice({', '.join(out)})"

    __repr__ = __str__

    def roll(self):
        output = []
        for num, faces in self.dice:
            rolls = [random.randint(1, faces) for _ in range(num)]
            output.append(
                sum(rolls) + sum(self.modifiers)
            )

        if len(output) == 1:
            return output[0]
        else:
            return output

    @property
    def average(self):
        """ Calculates the expected value of a sum of dice """
        roll_average = sum([num * (faces + 1) / 2 for num, faces in self.dice])
        return roll_average + sum(self.modifiers)

    @staticmethod
    def _parse(dice):
        """ Parses a single 'dice' string such as 'd6' or '5d20'

        Returns:
            tuple: Two values (a, b) where `a` is the number of dice and `b`
            is the number of faces on each die.
        """
        splits = dice.split("d")
        if len(splits) != 2:
            raise Exception(f"Unparseable dice string: {dice}")

        count, faces = splits
        if count == "":
            count = 1
        return (int(count), int(faces))


if __name__ == "__main__":
    print(Dice(["1d20", "1d10"]) + Modifier(1))
