""" Implementation of all spells """

from combatsim.dice import Dice
from combatsim.rules_error import RulesError
from combatsim.event import EventLog

LOGGER = EventLog()

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


class TargetType:

    def __init__(self, **kwargs):
        """ Stores information for the AI targeting.

        For example, the target type may include a max number of targets that
        the AI code will need to know about. By storing this information in the
        target type, the AI can check for a max and decide what creatures to
        target.

        Keyword Arguments:
            max (int): The maximum number of targets allowed
            filter (function):
        """
        self.max = kwargs.get('max', None)
        self.filter = kwargs.get('filter', None)


class Sphere(TargetType):
    """ Contains algorithms for calculating which targets are hit.

    There are two main uses of this class. First, you can use it to verify that
    a list of targets are all within a sphere of radius R. Second, you can use
    it to find all possible targets within a sphere centered at a specified
    position.

    Args:
        radius (int): Radius of the sphere.
        **kwargs: All additional keyword arguments will be passed to the
            TargetType base class. Please see that class for a list of allowed
            arguments.
    """

    def __init__(self, radius=5, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def contains(self, positions):
        """ Checks if all given positions are within a circle of radius R.

        R is the radius of the sphere passed into the constructor.

        Returns:
            True if all positions are within a circle of radius R. False
            otherwise.
        """
        pass


class Spell:
    """ Parent class for all spells.

    The __init__ method of this class is used to set up basic information about
    who is casting the spell and what level the spell is being cast at.
    """

    def __init__(
        self,
        name,
        casting_time="action",
        school="conjuration",
        level=0,
        range_=0,
        targeting=None,
        effects=None
    ):
        self.name = name
        self.casting_time = casting_time
        self.school = school
        self.range = range_

        if not targeting:
            self.targeting = Sphere()
        self.targeting = targeting

        if not effects:
            effects = []
        self.effects = effects

        self.level = level

    def cast(self, caster, level, *args, **kwargs):
        if self.level > level:
            raise RulesError(
                f"{self.name} must be cast at level {self.level} but "
                f"was cast at level {level}"
            )

        LOGGER.log(f"{caster} casts {self.name}")
        for effect in self.effects:
            message = effect.activate(
                caster, level, *args, **kwargs
            )


# TODO (phillip): Really good idea. I can have a "Targets" class that is what
# gets passed to effects. It usually just acts as a list, but it can also be a
# dictionary with filters. For instance, if you want all targets, you just do
#
#   for target in targets:
#       # do something
#
# but if you want just enemies, you could write
#
#   for target in targets['enemies']:
#       # do something


class Effect:
    """ An effect that can be triggered by a spell or trap.

    Attributes:
        target_type (str): This is how this spell targets creatures. There are
            currently 3 supported target types. `self` targets the caster.
            `target` targets a single creature including self. `targets will
            target all creatures passed to the activate method in the
            'targets' key. If you use the `targets` type, you can include
            'min_targets' and 'max_targets' in the `props` attribute.
        props (dict): A dictionary of dynamic properties used by the effect.
    """

    def __init__(self, props=None):
        if not props:
            props = {}
        self.props = props

    #def get_targets(self, **kwargs):
    #    if self.target_type == "targets":
    #        targets = kwargs.get('targets', [])
    #        min_targets = self.props.get('min_targets', None)
    #        max_targets = self.props.get('max_targets', None)

    #        if min_targets and len(targets) < min_targets:
    #            raise RulesError(
    #                f"{self} must target at least {min_targets} targets"
    #            )
    #        if max_targets and len(targets) > max_targets:
    #            raise RulesError(
    #                f"{self} must target at most {max_targets} targets"
    #            )

    #        return targets

    #    if self.target_type == "target":
    #        if 'target' in kwargs:
    #            return [kwargs['target']]
    #        else:
    #            return []

    #    if self.target_type == "self":
    #        return [kwargs['caster']]

    def activate(self, caster, level, **kwargs):
        raise NotImplementedError


class SavingThrow(Effect):

    # TODO (phillip): Implement half on fail
    def __init__(self, target_type, attribute, effect, **kwargs):
        super().__init__(target_type, **kwargs)
        self.attribute = attribute
        self.effect = effect

    def activate(self, caster, level, **kwargs):
        # TODO (phillip): Need to implement saving throw proficiency. This
        # logic should probably be moved to the `creature` class because the
        # creature itself will know when it has advantage/disadvantage or other
        # modifiers to the saving throw.
        for target in self.get_targets(caster=caster, **kwargs):
            # TODO (phillip): Not all effects should have an associated caster.
            # I may want to rethink this API.
            saved = target.saving_throw(self.attribute, caster.spell_dc)
            if not saved:
                self.effect.activate(caster, level, target=target)


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
class PipedEffect(Effect):
    """ Effects that can be piped into each other.

    For instance, if you want to inmplement a "drain" spell, you need to have
    the amount of damage piped to the Heal effect.
    """

    def __init__(self, target_type, pipe=None):
        super().__init__(target_type)
        self.pipe = pipe

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
            LOGGER.log(f"\thealing {target} by {actual_healing}")

        return actual_healing


class Damage(PipedEffect):

    def __init__(self, target_type, pipe=None, type_=None):
        super().__init__(target_type, pipe)
        self.damage_type = type_

    def activate(self, caster, level, **kwargs):
        # Get piped damage or roll the damage
        damage = super().activate(caster, level, **kwargs)
        if not damage:
            damage = sum((Dice("1d8") * level).roll()) + caster.spellcasting

        for target in self.get_targets(caster=caster, **kwargs):
            actual_damage = target.take_damage(damage, self.damage_type)
            LOGGER.log(f"\tdamaging {target} by {actual_damage}")

        return actual_damage


class CantripDamage(PipedEffect):
    levels = [1, 5,11,17]

    def __init__(self, target_type, dice, pipe=None, type_=None):
        super().__init__(target_type, pipe)
        self.damage_type = type_
        self.damage_dice = dice

    # TODO (phillip): This method is a lot like Damage.activate
    def activate(self, caster, target, level, **kwargs):
        # Get piped damage or roll the damage
        damage = super().activate(caster, level, **kwargs)
        if not damage:
            scale = sum([1 for x in CantripDamage.levels if x <= caster.level])
            damage = sum((self.damage_dice * scale).roll())

        actual_damage = target.take_damage(damage, self.damage_type)
        LOGGER.log(f"\tdamaging {target} by {actual_damage}")

        return actual_damage


