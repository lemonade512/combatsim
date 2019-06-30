""" My own custom monsters for testing encounters.  """

from combatsim.dice import Dice
from combatsim.tactics import Healer
from combatsim.spells import CureWounds
from combatsim.items import Weapon

simple_cleric = {
    'name': "Cleric",
    'level': 5,
    'weapons': [
        Weapon("Staff", Dice("1d6"), "bludgeoning", attack_mod=4, damage_mod=2)
    ],
    'spell_slots': [3],
    'spells': [CureWounds],
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
