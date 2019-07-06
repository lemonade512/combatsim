""" My own custom monsters for testing encounters.  """

from combatsim.dice import Dice
from combatsim.tactics import Healer, Mage
from combatsim.spells import acid_splash, cure_wounds, drain
from combatsim.items import Weapon

simple_cleric = {
    'name': "Cleric",
    'level': 5,
    'weapons': [
        Weapon("Staff", Dice("1d6"), "bludgeoning", attack_mod=4, damage_mod=2)
    ],
    'spell_slots': [3],
    'spells': [cure_wounds],
    'tactics': Healer
}

commoner = { 'name': "Commoner" }

knight = {
    'name': "Knight",
    'ac': 14,
    'level': 5,
    'strength': 14,
    'weapons': [
        Weapon("Longsword", Dice("1d8"), "slashing")
    ]
}

mage = {
    'name': "Mage",
    'ac': 12,
    'level': 2,
    'intelligence': 12,
    'spell_slots': [5],
    'spells': [acid_splash],
    'tactics': Mage
}
