""" Implementation of all spells """

from combatsim.dice import Dice
from combatsim.rules_error import RulesError
from combatsim.event import EventLog

# TODO event oriented programming. Spell effects can subscribe to "move" events from a character.
# Could also be especially useful for "tactics" classes that want to perform
# reactions on certain events.


class TargetList:
    """ Class with convenience filters passed to effects.

    For example, an effect may be filtered on specific targets such as enemies,
    allies, or something else. The TargetList class is responsible for
    providing the full list of targets and ways to filter those targets.
    """

    def __init__(self, targets=None):
        if not targets:
            self.targets = {'all': []}
        else:
            self.targets = targets

    def __iter__(self):
        for target in self.targets['all']:
            yield target

    def __getitem__(self, key):
        return self.targets[key]

    def add(self, target, tags=None):
        self.targets['all'].append(target)
        if not tags:
            return

        for tag in tags:
            if tag not in self.targets:
                self.targets[tag] = [target]
            else:
                self.targets[tag].append(target)


class Point:

    @staticmethod
    def dist_squared(p0, p1):
        return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2


class TargetGeometry:

    def __init__(self, **kwargs):
        """ Stores information for the AI targeting.

        For example, the target type may include a max number of targets that
        the AI code will need to know about. By storing this information in the
        target type, the AI can check for a max and decide what creatures to
        target.

        Keyword Arguments:
            max (int): The maximum number of targets allowed
            filter (str): A filler value that is currently not used.
        """
        self.max = kwargs.get('max_', None)
        self.filter = kwargs.get('filter_', None)

    def contains(self, positions):
        if self.max is None:
            return True
        if len(positions) > self.max:
            return False
        return True


class Sphere(TargetGeometry):
    """ Contains algorithms for calculating which targets are hit.

    There are two main uses of this class. First, you can use it to verify that
    a list of targets are all within a sphere of radius R. Second, you can use
    it to find all possible targets within a sphere centered at a specified
    position.

    Args:
        radius (int): Radius of the sphere.
        **kwargs: All additional keyword arguments will be passed to the
            TargetGeometry base class. Please see that class for a list of
            allowed arguments.
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
        if not super().contains(positions):
            return False
        if len(positions) <= 1:
            return True

        # First find the "bounding box" of the points
        x_vals = [p[0] for p in positions]
        y_vals = [p[1] for p in positions]
        x1, y1 = min(x_vals), min(y_vals)
        x2, y2 = max(x_vals), max(y_vals)

        # Next find the center point of the bounding box
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        # Finally, check to see if the distance to all positions is less than
        # the radius of the sphere
        for p in positions:
            if Point.dist_squared(p, (cx, cy)) > self.radius ** 2:
                return False

        return True


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
        components=None,
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
            targeting = Sphere()
        self.targeting = targeting

        if not effects:
            effects = []
        self.effects = effects

        self.level = level

    def cast(self, caster, level, targets):
        if self.level > level:
            raise RulesError(
                f"{self.name} must be cast at level {self.level} but "
                f"was cast at level {level}"
            )

        target_list = TargetList()
        for target in targets:
            tags = []
            if target.team is None or target.team != caster.team:
                tags.append('enemies')
            else:
                tags.append('allies')
            target_list.add(target, tags)

        pos_list = [(t.x, t.y) for t in target_list]
        if not self.targeting.contains(pos_list):
            raise RulesError(f"{self.targeting} does not contain {target_list}")

        for target in targets:
            if caster.distance_to(target) > self.range:
                raise RulesError(f"{target} is out of range of {caster}")

        EventLog.log(f"{caster} casts {self.name}")
        for effect in self.effects:
            message = effect.activate(
                caster, level, target_list
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
    """ An effect that can be triggered by a spell or trap. """

    def __init__(self, filters=None, max_=None):
        if filters is None:
            filters = []
        self.filters = filters

        self.max = max_

    def activate(self, caster, level, targets):
        raise NotImplementedError

    def filter(self, targets):
        for filter_ in self.filters:
            targets = targets[filter_]
        return targets


class SavingThrow(Effect):
    """ Rolls a saving throw before activating effects.

    A saving throw can either reduce the contained effects by some multiplier,
    or it can ignore any contained effects altogether. If you use a multiplier,
    the contained effects **must** accept a 'multiplier' keyword argument in
    their `activate` methods.
    """

    def __init__(self, attribute, effect, multiplier=None, **kwargs):
        super().__init__(**kwargs)
        self.attribute = attribute
        self.effect = effect
        self.multiplier = multiplier

    def activate(self, caster, level, targets):
        for target in targets:
            saved = target.saving_throw(self.attribute, caster.spell_dc)
            if not saved:
                self.effect.activate(caster, level, [target])
            elif saved and self.multiplier:
                self.effect.activate(
                    caster, level, [target], multiplier=self.multiplier
                )


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

    def __init__(self, pipe=None):
        super().__init__()
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
            EventLog.log(f"\thealing {target} by {actual_healing}")

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
            EventLog.log(f"\tdamaging {target} by {actual_damage}")

        return actual_damage


class CantripDamage(PipedEffect):
    levels = [1, 5,11,17]

    def __init__(self, dice, type_=None, **kwargs):
        super().__init__(**kwargs)
        self.damage_type = type_
        self.damage_dice = Dice(dice)

    # TODO (phillip): This method is a lot like Damage.activate
    def activate(self, caster, level, targets, **kwargs):
        # Get piped damage or roll the damage
        damage = super().activate(caster, level, **kwargs)
        if not damage:
            scale = sum([1 for x in CantripDamage.levels if x <= caster.level])
            damage = sum((self.damage_dice * scale).roll())

        actual_damage = 0
        for target in targets:
            actual_damage += target.take_damage(damage, self.damage_type)
            EventLog.log(f"\tdamaging {target} by {actual_damage}")

        return actual_damage


