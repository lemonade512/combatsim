""" Monsters from the basic rules of D&D.

This file should only contain monsters that are available under the open games
license. Any other monsters that are in the monster manual or other source
books should be kept in a private database.
"""

from combatsim.creature import Monster
from combatsim.items import Weapon
from combatsim.dice import Dice

# TODO (phillip): Implement range for light crossbow
bandit = {
    'name': "Bandit",
    'xp': 25,
    'level': 2,
    'strength': 11,
    'dexterity': 12,
    'constitution': 12,
    'intelligence': 10,
    'wisdom': 10,
    'charisma': 10,
    'hd': Dice("1d8"),
    'armor': Armor("Leather", 11),
    'weapons': [
        Weapon("Scimitar", Dice("1d6"), "slashing", attack_mod=3, damage_mod=1),
        Weapon("Light Crossbow", Dice("1d8"), "piercing", melee=False, attack_mod=3, damage_mod=1)
    ]
}

# TODO (phillip): Implement pack tactics
blood_hawk = {
    'name': "Blood Hawk",
    'xp': 25,
    'level': 2,
    'strength': 6,
    'dexterity': 14,
    'constitution': 10,
    'intelligence': 3,
    'wisdom': 14,
    'charisma': 5,
    'hd': Dice("1d6"),
    'ac': 12,
    'weapons': [
        Weapon("Beak", Dice("1d4"), "piercing", attack_mod=4, damage_mod=2)
    ]
}
