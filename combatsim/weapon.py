""" Defines data object for weapons. """

class Weapon:

    def __init__(self, name, ability, damage, damage_type):
        # TODO (phillip): allow for "finesse" weapons that can use either
        # dexterity or strength depending on what is higher. Perhaps, the
        # abilities could be a list, and the Rules could choose highest?
        self.name = name
        self.ability = ability
        self.damage = damage
        # TODO (phillip): Support multiple types of damage. Some weapons do
        # both slashing and poison for instance. Also, need to support weapons
        # that do damage then an effect of some sort (like stun)
        self.damage_type = damage_type


class Attack:
    """ A more general class than Weapon. """

    def __init__(self):
        # TODO (phillip): this was just an idea I had. For regular characters,
        # or simple NPCs, you can just pass in a weapon and have everything
        # automatically calculated when it is added to a creature (this would
        # require the creature __init__ method calling bind() or something)
        # However, you can also just pass in overriding values if you want.
        pass
