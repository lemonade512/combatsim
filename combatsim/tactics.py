""" AI implementations for basic characters and monsters.

All logic for deciding what spells to cast, what actions to take, and how to
move should be put in one of the `tactics` classes.
"""


class BaseTactics:

    def __init__(self, actor):
        self.actor = actor  # The creature these tactics will be for

    def allies(self, creatures):
        return [
            c for c in creatures
            if c.team == self.actor.team
            and c.team is not None
        ]

    def enemies(self, creatures):
        return [
            c for c in creatures
            if c.team != self.actor.team
            or c.team is None
        ]


class TargetWeakest(BaseTactics):

    def act(self, creatures):
        target = None
        for creature in self.enemies(creatures):
            if not creature.is_alive():
                continue

            if not target:
                target = creature
            elif creature.hp > 0 and creature.hp < target.hp:
                target = creature

        self.actor.attack(target, self.actor.weapons[0])


class Mage(TargetWeakest):

    def act(self, creatures):
        if self.actor.spell_slots[0] == 0:
            return super().act(creatures)

        possible_targets = [e for e in self.enemies(creatures) if e.hp > 0]
        return self.actor.cast(self.actor.spells[0], 0, targets=possible_targets[:2])


class Healer(TargetWeakest):

    def act(self, creatures):
        if self.actor.spell_slots[0] == 0:
            return super().act(creatures)

        if self.actor.hp < self.actor.max_hp:
            return self.actor.cast(self.actor.spells[0], 1, target=self.actor)

        for creature in self.allies(creatures):
            if creature.hp < creature.max_hp:
                return self.actor.cast(self.actor.spells[0], 1, target=creature)

        return super().act(creatures)
