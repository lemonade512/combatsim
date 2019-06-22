""" Defines a creature that can be used in the simulator. """

import math

from combatsim.dice import Dice, Modifier


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
        level (int): The level of the creature. Level only really makes sense
            for player characters and NPCs. Most creatures from the monster
            manual will be "level 1" but have a meaningful challenge rating.
        xp (int): How much xp this creature is worth.
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
        self.level = kwargs.get('level', 1)
        self.xp = kwargs.get('xp', None)
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
            'attacks', [(Dice("d20") + self.strength, Dice("d4") + self.strength)]
        )

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__

    def attack(self, other):
        weapon = self.attacks[0]
        roll = weapon[0].roll()[0]
        if roll >= other.ac:
            damage = weapon[1].roll()[0]
            print(f"{self} hits {other} with {roll} doing {damage} damage")
            other.hp -= damage
        else:
            print(f"{self} misses {other} with {roll}")

    def choose_target(self, others):
        for creature in others:
            if creature.hp > 0:
                return creature

        return None

    #def act(self, enemies, allies):
    def act(self, others):
        if not self.is_alive():
            return
        target = self.choose_target(others)
        self.attack(target)

    def is_alive(self):
        return self.hp > 0

    @property
    def stat_block(self):
        out = f"Creature({self.name})\n"
        out += f"\t==Abilities==\n"
        out += f"\t\tStr: {self.strength.value} ({self.strength.mod})"
        out += f"  Dex: {self.dexterity.value} ({self.dexterity.mod})"
        out += f"  Con: {self.constitution.value} ({self.constitution.mod})\n"
        out += f"\t\tInt: {self.intelligence.value} ({self.intelligence.mod})"
        out += f"  Wis: {self.wisdom.value} ({self.wisdom.mod})"
        out += f"  Cha: {self.charisma.value} ({self.charisma.mod})\n"
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
        # TODO (phillip): HP is calculated somewhat differently for monsters
        # than for PCs. Instead of level, monsters just have hit dice with
        # a modifier, and they don't use the max for "first level". I should
        # figure out a clean way to represent this difference. Inheritance of
        # some sort might be the issue (monster and player both inherit from
        # creature for instance)
        #
        # Note: It looks like most hit dice + mods for creatures are actually
        # calculated from an underlying level that isn't exposed to the DM.
        dice = self.hd + self.constitution
        if average:
            return round(dice.max + (dice * (self.level - 1)).average)

        rolls = (dice * (self.level - 1)).roll()
        return dice.max + sum(rolls)


if __name__ == "__main__":
    c = Creature(hd=Dice("1d8"), level=5, constitution=12, strength=15)
    print(c.stat_block)
