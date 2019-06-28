""" Defines data object for weapons. """

from combatsim.dice import Dice


class Attack:
    """ Generic representation of an attack method for a creature.

    Attributes:
        name (str): The name of this attack
        damage (Dice): Dice without any modifiers for this attack
        damage_type (str): The type of damage this weapon does.
        melee (bool): True if this is a melee weapon.
        owner (Creature): The creature who has this weapon equipped.
        properties (list): A list of property tags.
    """

    def __init__(self, name, damage, damage_type, melee=True, owner=None, properties=None):
        self.name = name
        self.damage = damage
        self.damage_type = damage_type
        self.melee = melee
        self.owner = owner  # Creature that has this attack 'equipped'
        if not properties:
            properties = {}
        self.properties = properties

    def attack_roll(self, advantage=False, disadvantage=False):
        if advantage and disadvantage:
            advantage = False
            disadvantage = False

        dice = Dice("1d20")
        dice_mod = self._get_ability()
        if self.owner.is_proficient(self):
            dice_mod += self.owner.proficiency

        if advantage:
            roll = max((dice * 2).roll())
        elif disadvantage:
            roll = min((dice * 2).roll())
        else:
            roll = dice.roll()[0]

        return roll + dice_mod, roll == 20

    def damage_roll(self, crit=False):
        dice = self.damage
        if crit:
            dice = dice * 2

        return sum(dice.roll()) + self._get_ability(), self.damage_type

    def _get_ability(self):
        if 'finesse' in self.properties:
            return max(self.owner.strength, self.owner.dexterity)
        elif self.melee:
            return self.owner.strength
        else:
            return self.owner.dexterity
