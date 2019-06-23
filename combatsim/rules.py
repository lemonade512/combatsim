""" Define basic rules for attacking, casting spells, etc.

This will throw exceptions if a rule is violated at any point. For example,
if a creature tries to cast a spell when it has no spell slots, a rule
exception will be thrown.
"""

from combatsim.dice import Dice


class Rules:

    @staticmethod
    def attack(attacker, target, weapon):
        attack_dice = Dice("d20") + attacker.attributes[weapon.ability]
        if attacker.is_proficient(weapon):
            attack_dice += attacker.proficiency
        roll = attack_dice.roll()[0]
        if roll >= target.ac:
            damage_dice = weapon.damage + attacker.attributes[weapon.ability]
            damage = damage_dice.roll()[0]
            print(f"{attacker} hits {target} with {weapon.name} doing {damage} damage")
            target.hp -= damage
        else:
            print(f"{attacker} misses {target} with {weapon.name}")
