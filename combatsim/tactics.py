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

        Rules.attack(self.actor, target, self.actor.attacks[0])
