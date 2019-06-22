""" Define basic rules for attacking, casting spells, etc.

This will throw exceptions if a rule is violated at any point. For example,
if a creature tries to cast a spell when it has no spell slots, a rule
exception will be thrown.
"""


class Rules:

    @staticmethod
    def attack(attacker, target, weapon):
        roll = weapon[0].roll()[0]
        if roll >= target.ac:
            damage = weapon[1].roll()[0]
            print(f"{attacker} hits {target} with {roll} doing {damage} damage")
            target.hp -= damage
        else:
            print(f"{attacker} misses {target} with {roll}")
