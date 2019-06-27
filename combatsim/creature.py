""" Defines a creature that can be used in the simulator. """

import math

from combatsim.dice import Dice, Modifier
from combatsim.rules import Rules
from combatsim.tactics import TargetWeakest
from combatsim.weapon import Weapon


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
        return f"{self.value} ({self.mod})"

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


# TODO (phillip): Figure out a good way to specify base creature
class Creature:
    """ Definition of a creature and its stats.

    Attributes:
        name (str): The creatures name. This should be unique if you want to
            tell different creatures apart when simulating an encounter.
        xp (int): How much xp this creature is worth.
        level (int): The level of the creature. Level only really makes sense
            for player characters and NPCs. Most creatures from the monster
            manual will be "level 1" but have a meaningful challenge rating.
        proficiency (int): This is the creature's proficiency modifier. It can
            be added to dice rolls that a creature is proficient in.
        max_hp (int): Max HP of the creature.
        hp (int): Current HP of the creature.
        hd (Dice): The hit die used by this creature. This should not have any
            modifiers attached to it. # TODO (phillip) I could maybe attach the
            constitution modifier to this? The only downside I can think of is
            that users will need to remember to add constitution modifier when
            passing the hd into the __init__ method.
        strength (Ability): Strength ability score
        dexterity (Ability): Dexterity ability score
        constitution (Ability): Constitution ability score
        intelligence (Ability): Intelligence ability score
        wisdom (Ability): Wisdom ability score
        charisma (Ability): Charisma ability score
        ac (int): Armor class of the creature.
        initiative (Dice): The dice + modifiers to roll for this creatures
            initiative in combat.
        attacks (list): A list of (Dice, Dice) tuples where the first value
            is the dice to roll for the attack with modifiers, and the
            second value is the damage dice to roll on a hit.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "nameless")
        self.xp = kwargs.get('xp', None)
        self.level = kwargs.get('level', 1)
        self.proficiency = kwargs.get(
            'proficiency', 1 + math.ceil(self.level / 4)
        )
        self.strength = Ability("Strength", kwargs.get('strength', 10))
        self.dexterity = Ability("Dexterity", kwargs.get('dexterity', 10))
        self.constitution = Ability(
            "Constitution", kwargs.get('constitution', 10)
        )
        self.intelligence = Ability(
            "Intelligence", kwargs.get('intelligence', 10)
        )
        self.wisdom = Ability("Wisdom", kwargs.get('wisdom', 10))
        self.charisma = Ability("Charisma", kwargs.get('charisma', 10))
        self.attributes = {
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma
        }
        self.hd = kwargs.get('hd', Dice('1d8'))

        # Must come after hd and abilities so _calc_hp works properly
        self.max_hp = kwargs.get('max_hp', self._calc_hp())
        self.hp = self.max_hp

        # TODO (phillip): Make this calculated based on the armor worn and the
        # creature's dexterity. Also, figure out how to include temp spell
        # effects
        self.ac = kwargs.get('ac', 10)
        self.initiative = kwargs.get(
            'initiative', Dice("d20") + self.dexterity
        )

        # TODO (phillip): Implement weapons so that we can have attack damage
        # types, weapon names, and other attack options.
        self.attacks = kwargs.get(
            'attacks', [Weapon('Dagger', 'strength', Dice('1d4'), 'piercing')]
        )
        self.tactics = kwargs.get('tactics', TargetWeakest)(self)
        self.team = kwargs.get('team', None)
        self.resistances = kwargs.get('resistances', [])
        self.spellcasting = self.attributes[
            kwargs.get('spellcasting', 'wisdom')
        ]
        self.spells = kwargs.get('spells', [])
        self.spell_slots = {
            1: 4,
            2: 4
        }

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__

    def is_proficient(self, weapon):
        # TODO (phillip): Implement this
        return True

    def is_alive(self):
        return self.hp > 0

    @property
    def stat_block(self):
        out = f"Creature({self.name})\n"
        out += f"\t==Abilities==\n"
        out += f"\t\tStr: {self.strength}"
        out += f"  Dex: {self.dexterity}"
        out += f"  Con: {self.constitution}\n"
        out += f"\t\tInt: {self.intelligence}"
        out += f"  Wis: {self.wisdom}"
        out += f"  Cha: {self.charisma}\n"
        out += f"\t==Attacks==\n"
        for attack in self.attacks:
            out += f"\t\t{attack}"
        return out

    def _calc_hp(self, average=False):
        """ Calculate HP of this creature.

        By default, this will roll for this creature's max hitpoints.

        Args:
            average (bool): Whether or not to take the average.
        """
        raise NotImplementedError

    def attack(self, target, weapon):
        # TODO (phillip): These rules work well for PCs, but some monsters
        # don't follow these rules for calculating the modifier when rolling to
        # hit. Perhaps, I should just include the "to-hit" bonus with the
        # weapon? Or maybe add it as part of an "attack" object?
        attack_dice = Dice("d20") + self.attributes[weapon.ability]
        if self.is_proficient(weapon):
            attack_dice += self.proficiency
        roll = attack_dice.roll()[0]
        if roll >= target.ac:
            damage = (weapon.damage + self.attributes[weapon.ability]).roll()[0]
            damage_taken = target.take_damage(damage, weapon.damage_type)
            print(f"{self} hits {target} with {weapon.name} doing {damage_taken} damage")
        else:
            print(f"{self} misses {target} with {weapon.name}")

    def take_damage(self, value, type_=None):
        """ Take damage of a given type.

        This function will check for resistances and other effects to calculate
        the actual damage taken. When damage reduces the creature to 0 HP, and
        there is damage remaining, the creature dies if the remaining damage
        equals or exceeds its hitpoint maximum.

        Returns:
            str: A string representing the damage taken after resistances.
        """
        if type_ in self.resistances:
            taken = math.floor(value / 2)
            expression = f"{value} / 2 = {taken}"
        else:
            taken = value
            expression = f"{value}"

        self.hp -= taken
        if self.hp < -self.max_hp:
            # TODO (phillip): Implement creature death
            pass

        self.hp = max(0, self.hp)
        return expression

    def heal(self, value):
        add = min(self.max_hp - self.hp, value)
        self.hp += add
        return add


class Monster(Creature):
    """ Represents NPCs or Monsters run by the DM.

    There are a few differences in how monsters work from how player characters
    work. For one, monster hitpoints are calculated from hit dice differently
    than for players.
    """

    def _calc_hp(self, average=False):
        dice = self.hd + self.constitution
        if average:
            return round((dice * self.level).average)

        return sum((dice * self.level).roll())


class Character(Creature):
    """ Represents a player character.

    Characters have all the attributes of a Creature, but also have a few
    additional attributes as defined below.

    Attributes:
    """

    def _calc_hp(self, average=False):
        dice = self.hd + self.constitution
        if average:
            return round(dice.max + (dice * (self.level - 1)).average)

        return dice.max + sum((dice * (self.level-1)).roll())


if __name__ == "__main__":
    c = Monster(hd=Dice("1d8"), level=6, constitution=15, strength=15)
    p = Character(hd=Dice("1d8"), level=6, constitution=15)
    print(c.max_hp)
    print(p.max_hp)
