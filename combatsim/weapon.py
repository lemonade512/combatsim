""" Defines data object for weapons. """

class Weapon:

    def __init__(self, name, ability, damage, damage_type):
        self.name = name
        self.ability = ability
        self.damage = damage
        self.damage_type = damage_type
