""" Define basic rules for attacking, casting spells, etc.

This will throw exceptions if a rule is violated at any point. For example,
if a creature tries to cast a spell when it has no spell slots, a rule
exception will be thrown.
"""

import math

from combatsim.dice import Dice


class RulesError(Exception):
    """ Exception raised when a rule is broken. """
    pass


class Rules:

    @staticmethod
    def cast(caster, level, spell, *args, **kwargs):
        """ Casts a spell.

        Args:
            caster (Creature): The creature that is casting the spell.
            level (int): The level this spell is being cast at.
            spell (type): The class of spell being cast.
        """
        if level > 0:
            if caster.spell_slots[level] < 1:
                raise RulesError(
                    f"{caster} has no more level {level} spell slots"
                )
            caster.spell_slots[level] -= 1

        if spell.min_level > level:
            raise RulesError(
                f"{spell.__name__} must be cast at level {spell.min_level} but "
                f"was cast at level {level}"
            )

        spell(caster, level).cast(*args, **kwargs)
