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
class PipedEffect(Effect):
    """ Effects that can be piped into each other.

    For instance, if you want to inmplement a "drain" spell, you need to have
    the amount of damage piped to the Heal effect.
    """

    def __init__(self, target_type, effect=None):
        super().__init__(target_type)
        self.pipe = effect

    def activate(self, caster, level, **kwargs):
        if self.pipe:
            return self.pipe.activate(caster, level, **kwargs)
        return None


class Heal(PipedEffect):

    def activate(self, caster, level, **kwargs):
        # Get piped healing or roll the healing
        healing = super().activate(caster, level, **kwargs)
        if not healing:
            healing = sum((Dice("1d8") * level).roll()) + caster.spellcasting

        for target in self.get_targets(caster=caster, **kwargs):
            actual_healing = target.heal(healing)
            print(f"\thealing {target} by {actual_healing}")

        return actual_healing


class Damage(PipedEffect):

    def activate(self, caster, level, **kwargs):
        # Get piped damage or roll the damage
        damage = super().activate(caster, level, **kwargs)
        if not damage:
            damage = sum((Dice("1d8") * level).roll()) + caster.spellcasting

        for target in self.get_targets(caster=caster, **kwargs):
            actual_damage = target.take_damage(damage)
            print(f"\tdamaging {target} by {actual_damage}")

        return actual_damage


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


#cure_wounds = Spell("Cure Wounds", effects=[Heal('target'), Damage('self')])
drain = Spell("Drain", effects=[Damage('self', Heal('target'))])
cure_wounds = Spell("Cure Wounds", effects=[Heal('target')])
