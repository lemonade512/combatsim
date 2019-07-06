""" Implementation of all spells """

from combatsim.dice import Dice
from combatsim.rules_error import RulesError

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

    def __init__(self, target_type, props=None):
        self.target_type = target_type
        if not props:
            props = {}
        self.props = props

    def get_targets(self, **kwargs):
        if self.target_type == "targets":
            targets = kwargs.get('targets', [])
            min_targets = self.props.get('min_targets', None)
            max_targets = self.props.get('max_targets', None)

            if min_targets and len(targets) < min_targets:
                raise RulesError(
                    f"{self} must target at least {min_targets} targets"
                )
            if max_targets and len(targets) > max_targets:
                raise RulesError(
                    f"{self} must target at most {max_targets} targets"
                )

            return targets

        if self.target_type == "target":
            if 'target' in kwargs:
                return [kwargs['target']]
            else:
                return []

        if self.target_type == "self":
            return [kwargs['caster']]

    def activate(self, caster, level, **kwargs):
        raise NotImplementedError


class SavingThrow(Effect):

    # TODO (phillip): Implement half on fail
    def __init__(self, target_type, attribute, dc, effect, **kwargs):
        super().__init__(target_type, **kwargs)
        self.attribute = attribute
        # TODO (phillip): Instead of passing the DC, perhaps we should use the
        # caster's spell DC?
        self.dc = dc
        self.effect = effect

    def activate(self, caster, level, **kwargs):
        # TODO (phillip): Need to implement saving throw proficiency. This
        # logic should probably be moved to the `creature` class because the
        # creature itself will know when it has advantage/disadvantage or other
        # modifiers to the saving throw.
        for target in self.get_targets(caster=caster, **kwargs):
            saving_throw = (Dice("1d20") + target.attributes[self.attribute]).roll()[0]
            if saving_throw >= self.dc:
                print(f"\t{target} saved against {self.attribute} with a {saving_throw}")
                continue

            # TODO (phillip): Not all effects should have an associated caster.
            # I may want to rethink this API.
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
            print(f"\thealing {target} by {actual_healing}")

        return actual_healing


class Damage(PipedEffect):

    def __init__(self, target_type, pipe=None, type_=None):
        super().__init__(target_type, pipe)
        self.damage_type = type_

    def activate(self, caster, level, **kwargs):
        # TODO (phillip): Remove this and fix it for cantrips
        if level == 0:
            level = 5

        # Get piped damage or roll the damage
        damage = super().activate(caster, level, **kwargs)
        if not damage:
            damage = sum((Dice("1d8") * level).roll()) + caster.spellcasting

        for target in self.get_targets(caster=caster, **kwargs):
            actual_damage = target.take_damage(damage, self.damage_type)
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


# One or two targets within 5 feet of each other
# Dex save or take 1d6 damage (changes as level up)
# TODO (phillip): Targets must be within 5 feet of each other for acid splash
# TODO (phillip): Damage changes based on caster level for acid splash
# TODO (phillip): Creature must make dex save (no damage on pass, full damage on fail)
acid_splash = Spell(
    "Acid Splash",
    effects=[
        SavingThrow('targets', 'dexterity', 12, Damage('target', type_='acid'), props={
            'max_targets': 2
        })
    ],
    cantrip=True
)
drain = Spell("Drain", effects=[Damage('self', Heal('target'))])
cure_wounds = Spell("Cure Wounds", effects=[Heal('target')])
