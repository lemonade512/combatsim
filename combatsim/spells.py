""" Implementation of all spells """

from combatsim.dice import Dice


class Spell:
    """ Parent class for all spells.

    The __init__ method of this class is used to set up basic information about
    who is casting the spell and what level the spell is being cast at.
    """

    def __init__(self, caster, level, name=None):
        self.caster = caster
        self.level = level
        if not name:
            name = type(self).__name__
        self.name = name


class CureWounds(Spell):
    min_level = 1

    def cast(self, target):
        healing = sum((Dice("1d8") * self.level).roll()) + self.caster.spellcasting
        health = target.heal(healing)
        print(f"{self.caster} casts {self.name} healing {target} by {health}")
        print(f"{target} is now at {target.hp}")
