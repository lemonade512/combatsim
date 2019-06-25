""" Define basic rules for attacking, casting spells, etc.

This will throw exceptions if a rule is violated at any point. For example,
if a creature tries to cast a spell when it has no spell slots, a rule
exception will be thrown.
"""

import math

from combatsim.dice import Dice


class Rules:

    @staticmethod
    def attack(attacker, target, weapon):
        # TODO (phillip): These rules work well for PCs, but some monsters
        # don't follow these rules for calculating the modifier when rolling to
        # hit. Perhaps, I should just include the "to-hit" bonus with the
        # weapon? Or maybe add it as part of an "attack" object?
        attack_dice = Dice("d20") + attacker.attributes[weapon.ability]
        if attacker.is_proficient(weapon):
            attack_dice += attacker.proficiency
        roll = attack_dice.roll()[0]
        if roll >= target.ac:
            damage_dice = weapon.damage + attacker.attributes[weapon.ability]
            damage = damage_dice.roll()[0]
            if weapon.damage_type in target.resistances:
                prev_damage = damage
                damage = math.floor(damage / 2)
                print(
                    f"{attacker} hits {target} with "
                    f"{weapon.name} doing {prev_damage} / 2 = {damage} damage"
                )
            else:
                print(f"{attacker} hits {target} with {weapon.name} doing {damage} damage")
            target.hp -= damage
            print(f"{target} is now at {target.hp}")
        else:
            print(f"{attacker} misses {target} with {weapon.name}")
