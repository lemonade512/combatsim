""" Defines a creature that can be used in the simulator. """

import math

from combatsim.dice import Dice, Modifier
from combatsim.tactics import TargetWeakest
from combatsim.items import Armor, Weapon
from combatsim.rules_error import RulesError


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
        return f"Ability({self.value}, ({self.mod}))"

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
        ac (int): Armor class of the creature. By default, this number is the
            creature's base AC. However, if the creature is wearing armor, then
            it is the armor's base AC + the creature's dexterity. The max dex
            bonus for the armor is also taken into account.
        initiative (Dice): The dice + modifiers to roll for this creatures
            initiative in combat.
        attacks (list): A list of (Dice, Dice) tuples where the first value
            is the dice to roll for the attack with modifiers, and the
            second value is the damage dice to roll on a hit.
    """

    @classmethod
    def from_base(cls, base, **kwargs):
        """ Creates new monster from base template. """
        template = base
        base.update(kwargs)
        return cls(**template)

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
        self.hp = kwargs.get('hp', self.max_hp)

        self.armor = None
        armor = kwargs.get('armor', None)
        if 'ac' in kwargs:
            armor = Armor("Default", kwargs['ac'], 0)
        self.equip(armor)

        self.initiative = kwargs.get(
            'initiative', Dice("d20") + self.dexterity
        )

        # TODO (phillip): This part looks very similar to the armor part above.
        # Is there a way we can make this more elegant for both?
        self.weapons = []
        weapons = kwargs.get('weapons', [])
        for weapon in weapons:
            self.equip(weapon)
        if not self.weapons:
            self.equip(Weapon("Fists", Dice("1d4"), "bludgeoning"))

        self.tactics = kwargs.get('tactics', TargetWeakest)(self)
        self.team = kwargs.get('team', None)
        self.resistances = kwargs.get('resistances', [])
        self.spellcasting = self.attributes[
            kwargs.get('spellcasting', 'wisdom')
        ]
        self.spells = kwargs.get('spells', [])
        self.spell_slots = kwargs.get('spell_slots', [])

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__

    @property
    def ac(self):
        """ Calculated value of this creature's Armor Class.

        By default, this will simply be the Base AC for the creature, which
        allows us to specify the AC of any creature without worrying about
        what kind of armor they are wearing.

        If a creature does wear armor, or you want to specify the type of
        armor that a creature is wearing, then this function will calculate
        armor class from the item in the `armor` attribute and the dex mod.

            >>> chain = Armor("Chain Shirt", 13, 2)
            >>> Creature(armor=Armor("Natural", 15, 0)).ac == 15
            >>> Creature(armor=chain).ac == 13
            >>> Creature(armor=chain, dexterity=15).ac == 15
            >>> Creature(armor=chain, dexterity=20).ac == 15
        """
        if self.armor:
            return self.armor.ac
        return 10 + self.dexterity

    @property
    def spell_dc(self):
        """ DC for spells cast by this creature.  """
        return 8 + self.spellcasting + self.proficiency

    def saving_throw(self, attribute, dc):
        """ Rolls a saving throw for an attribute.

        Returns:
            bool: True if saved, False otherwise.
        """
        saving_throw = (Dice("1d20") + self.attributes[attribute]).roll()[0]
        if saving_throw >= dc:
            print(f"\t{self} saved against {attribute} with a {saving_throw}")
            return True
        else:
            return False

    def is_proficient(self, weapon):
        raise NotImplementedError

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
        dice = self.hd + self.constitution
        if average:
            return round((dice * self.level).average)

        return max(sum((dice * self.level).roll()), 1)

    def attack(self, target, attack):
        attack_roll, crit = attack.attack_roll()
        if attack_roll >= target.ac:
            damage, damage_type = attack.damage_roll(crit=crit)
            damage_taken = target.take_damage(damage, damage_type)
            print(f"{self} hits {target} with {attack.name} doing {damage_taken} damage")
        else:
            print(f"{self} misses {target} with {attack.name}")

    def cast(self, spell, level, *args, **kwargs):
        """ Casts a spell.

        Args:
            caster (Creature): The creature that is casting the spell.
            level (int): The level this spell is being cast at.
            spell (type): The class of spell being cast.
        """
        if spell not in self.spells:
            raise RulesError(
                f"{self} does not know the spell `{spell}`"
            )

        if level > 0:
            if len(self.spell_slots) < level:
                raise RulesError(
                    f"{self} does not have any level {level} spell slots"
                )
            if self.spell_slots[level-1] < 1:
                raise RulesError(
                    f"{self} has no more level {level} spell slots"
                )
            self.spell_slots[level-1] -= 1

        spell.cast(self, level, *args, **kwargs)

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
            # TODO (phillip): event log should show that damage was reduced
        else:
            taken = value

        # Only used to return at the end
        actual_taken = min(self.hp, taken)

        self.hp -= taken
        if self.hp < -self.max_hp:
            # TODO (phillip): Implement creature death
            pass

        self.hp = max(0, self.hp)
        return actual_taken

    def heal(self, value):
        add = min(self.max_hp - self.hp, value)
        self.hp += add
        return add

    def equip(self, item):
        if not item:
            return
        item.equip(self)


class Monster(Creature):
    """ Represents NPCs or Monsters run by the DM.

    There are a few differences in how monsters work from how player characters
    work. For one, monster hitpoints are calculated from hit dice differently
    than for players.
    """

    def is_proficient(self, weapon):
        # TODO (phillip): Implement this
        return False


class Character(Creature):
    """ Represents a player character.

    Characters have all the attributes of a Creature, but also have a few
    additional attributes as defined below.

    Attributes:
    """

    def is_proficient(self, weapon):
        # TODO (phillip): Implement this
        return True

    def _calc_hp(self, average=False):
        dice = self.hd + self.constitution
        if average:
            return max(round(dice.max + (dice * (self.level - 1)).average), 1)

        return max(dice.max + sum((dice * (self.level-1)).roll()), 1)
