from combatsim.dice import Dice

# TODO (phillip): When equipping an item, consider the following:
#   * What happens when you have two items that give the same effect, and one is un-equipped
#   * What happens when dual wielding the same type of weapon


class Item:

    def __init__(self, name, owner=None):
        self.name = name
        self.owner = owner

    def equip(self, creature):
        self.owner = creature


class Armor(Item):

    def __init__(self, name, base_ac, max_dex, **kwargs):
        super().__init__(name, **kwargs)
        self.base_ac = base_ac
        self.max_dex = max_dex

    @property
    def ac(self):
        return self.base_ac + min(self.max_dex, self.owner.dexterity)

    def equip(self, creature):
        # TODO (phillip): Check to see if the creature already has armor
        # equipped. There may be something that needs to be done in that
        # case.
        super().equip(creature)
        creature.armor = self


class Weapon(Item):
    """ Generic representation of an attack method for a creature.

    A weapon doesn't necessarily have to be an "item" of sorts. A natural
    weapon (such as claws) will use this class as well.

    Attributes:
        name (str): The name of this attack
        damage (Dice): Dice without any modifiers for this attack
        damage_type (str): The type of damage this weapon does.
        melee (bool): True if this is a melee weapon.
        owner (Creature): The creature who has this weapon equipped.
        properties (list): A list of property tags.
    """

    def __init__(
        self,
        name,
        damage,
        damage_type,
        melee=True,
        owner=None,
        properties=None
    ):
        super().__init__(name, owner)
        self.damage = damage
        self.damage_type = damage_type
        self.melee = melee
        if not properties:
            properties = []
        self.properties = properties

    def equip(self, creature):
        super().equip(creature)
        creature.weapons.append(self)

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
