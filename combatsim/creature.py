""" Defines a creature that can be used in the simulator. """

import math

from combatsim.dice import Dice

# Attributes:
#   Name, level, xp, proficiency, abilities, HD, HP,
#   AC, initiative, attacks

# Ignoring for now:
#   spellcasting


# TODO (phillip): Figure out a good way to specify base creature
class Creature:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "nameless")
        self.level = kwargs.get('level', 0)
        self.xp = kwargs.get('xp', None)
        self.proficiency = kwargs.get(
            'proficiency', 1 + math.ceil(self.level / 4)
        )
        self.hp = kwargs.get('hp', 10)
        self._strength = kwargs.get('strength', 10)
        self._dexterity = kwargs.get('dexterity', 10)
        self._constitution = kwargs.get('constitution', 10)
        self._intelligence = kwargs.get('intelligence', 10)
        self._wisdom = kwargs.get('wisdom', 10)
        self._charisma = kwargs.get('charisma', 10)

    @property
    def str(self):
        """ Strength ability modifier """
        return self._ability_bonus(self._strength)

    @property
    def dex(self):
        """ Dexterity ability modifier """
        return self._ability_bonus(self._dexterity)

    @property
    def con(self):
        """ Constitution ability modifier """
        return self._ability_bonus(self._constitution)

    @property
    def int(self):
        """ Intelligence ability modifer """
        return self._ability_bonus(self._intelligence)

    @property
    def wis(self):
        """ Wisdom ability modifier """
        return self._ability_bonus(self._wisdom)

    @property
    def cha(self):
        """ Charisma ability modifier """
        return self._ability_bonus(self._charisma)

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__

    def attack(self, other):
        print(f"{self} attacks {other}")
        other.hp -= 5

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

    @staticmethod
    def _ability_bonus(ability):
        return math.floor(int(ability) / 2 - 5)

    @property
    def stat_block(self):
        out = f"Creature({self.name})\n"
        out += f"\tStr: {self.strength} ({self._ability_bonus(self.strength)})"
        out += f"  Dex: {self.dexterity} ({self._ability_bonus(self.dexterity)})"
        out += f"  Con: {self.constitution} ({self._ability_bonus(self.constitution)})"
        out += f"\n\tInt: {self.intelligence} ({self._ability_bonus(self.intelligence)})"
        out += f"  Wis: {self.wisdom} ({self._ability_bonus(self.wisdom)})"
        out += f"  Cha: {self.charisma} ({self._ability_bonus(self.charisma)})"
        return out


if __name__ == "__main__":
    c = Creature()
    print(c.stat_block)
