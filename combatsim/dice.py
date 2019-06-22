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


class Dice:

    def __init__(self, dice, modifiers=None):
        if isinstance(dice, str):
            dice = [dice]
        self.dice = dice

        if not modifiers:
            modifiers = []
        self.modifiers = modifiers

    def __add__(self, other):
        if isinstance(other, Modifier):
            return Dice(self.dice, self.modifiers + [other])

        return NotImplemented

    def roll(self):
        output = []
        for d in self.dice:
            num, faces = Dice._parse(d)
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
        parsed = [Dice._parse(d) for d in self.dice]
        roll_average = sum([num * (faces + 1) / 2 for num, faces in parsed])
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
    print(Dice.roll('1d20'))
    print(Dice.roll(['1d6', 'd8', '2d10']))
    print(Dice.sum(['2d6', '5d8']))
