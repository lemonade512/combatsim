from combatsim.rules import Rules


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
        if not self.actor.is_alive():
            return

        target = None
        for creature in self.enemies(creatures):
            if not creature.is_alive():
                continue

            if not target:
                target = creature
            elif creature.hp > 0 and creature.hp < target.hp:
                target = creature

        self.actor.attack(target, self.actor.attacks[0])


class Healer(TargetWeakest):

    def act(self, creatures):
        if not self.actor.is_alive():
            return

        if self.actor.spell_slots[1] == 0:
            return super().act(creatures)

        if self.actor.hp < self.actor.max_hp:
            return Rules.cast(self.actor, 1, self.actor.spells[0], target=self.actor)

        for creature in self.allies(creatures):
            if creature.hp < creature.max_hp:
                return Rules.cast(self.actor, 1, self.actor.spells[0], target=creature)

        return super().act(creatures)
