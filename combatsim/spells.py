""" Implementation of all spells """

from combatsim.dice import Dice

# Example Spell:
#   level: 1
#   casting time: Reaction
#   range: self, 30 ft., 40 ft. cube
#   components
#

# Spell Types:
#   1) Instantaneous offensive AoE spells (eg. fireball)
#   2) Reactionary defensive spells (eg. shield, counterspell)
#   3) Instantaneous offensive targeted spells (eg. acid arrow)
#   4) ...

# TODO event oriented programming. Spell effects can subscribe to "move" events from a character.
# Could also be especially useful for "tactics" classes that want to perform
# reactions on certain events.


class Effect:

    def __init__(self, target_type):
        self.target_type = target_type

    def get_targets(self, **kwargs):
        if self.target_type == "target":
            if 'target' in kwargs:
                return [kwargs['target']]
            else:
                return []

        if self.target_type == "self":
            return [kwargs['caster']]

# TODO (philip): Spells could have a "dry run" function that will return a
# list of outcomes such as:
#
#   [
#       "damage {enemy 1}"
#       "heal {ally 2}"
#   ]
#
# Then, my tactics and AI could do dry runs of spells and have some sort of
# fitness function to determine which spell is best to cast.

# TODO (phillip): Should there be a Query class for querying for specific
# monsters or objects. There are spells that only affect undead. There are
# spells that affect all allies within a region. There are spells that
# effect allies in one way and enemies in a different way.

# TODO (phillip): Maybe effects should have activation conditions? For example,
# each turn we may check for an effect to become active or to dissipate. These
# could be defined by "activation" conditions.
#
# Another use for activation conditions might be saving throws.

# OR TODO TODO TODO: A GOOD IDEA might be to have composable effects where I
# can do SavingThrow(Heal('target'), dc=15, 'dexterity') or something like that

# TODO (phillip): I have used "target_type" on the Effect class to extract out
# the logic for choosing targets. I should figure out how to extract out the
# need to hardcode the dice used, the level multiplication, and the caster
# spellcasting modifier.
class Heal(Effect):

    def activate(self, caster, level, **kwargs):
        healing = sum((Dice("1d8") * level).roll()) + caster.spellcasting
        for target in self.get_targets(caster=caster, **kwargs):
            health = target.heal(healing)

        return f"healing {target} by {health}"


class Damage(Effect):

    def activate(self, caster, level, **kwargs):
        damage = sum((Dice("1d8") * level).roll()) + caster.spellcasting
        for target in self.get_targets(caster=caster, **kwargs):
            target.take_damage(damage)
            return f"damaging {target} by {damage}"


class Spell:
    """ Parent class for all spells.

    The __init__ method of this class is used to set up basic information about
    who is casting the spell and what level the spell is being cast at.
    """

    def __init__(self, name=None, effects=None, level=1, cantrip=False):
        if not name:
            name = type(self).__name__
        self.name = name

        if not effects:
            effects = []
        self.effects = effects

        self.level = level
        self.cantrip = cantrip

    def cast(self, caster, level, *args, **kwargs):
        if not self.cantrip and self.level > level:
            raise RulesError(
                f"{self.name} must be cast at level {self.level} but "
                f"was cast at level {level}"
            )

        print(f"{caster} casts {self.name}")
        for effect in self.effects:
            message = effect.activate(
                caster, level, *args, **kwargs
            )
            print(f"\t{message}")


cure_wounds = Spell("Cure Wounds", effects=[Heal('target'), Damage('self')])
