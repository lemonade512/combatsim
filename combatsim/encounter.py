from collections import defaultdict

from combatsim.dice import Dice
from combatsim.tactics import Healer
from combatsim.event import EventLog

class Encounter:

    def __init__(self, creatures):
        self.creatures = creatures
        self.combat_round = 0

    def run(self):
        print("==== Combatants ====")
        event_log = EventLog()
        event_log.encounter = self
        for creature in self.creatures:
            print(f"{creature}: {creature.hp}")

        print("\n==== BEGIN ENCOUNTER ====")
        initiative = self.roll_initiative()
        while not self.encounter_over():
            self.combat_round += 1
            for init, creature in initiative:
                if creature.hp > 0:
                    creature.tactics.act(
                        [c for c in self.creatures if c != creature]
                    )
        print(event_log)

        print("\n==== END ENCOUNTER ====")
        for creature in self.creatures:
            print(f"\t{creature}: {creature.hp}")

    def encounter_over(self):
        """ Returns true if all creatures on all but one team are dead. """
        teams = defaultdict(int)
        for creature in self.creatures:
            if not creature.is_alive():
                continue
            teams[creature.team] += 1
        return len(teams) <= 1 and teams[None] <= 1

    def roll_initiative(self):
        """ Rolls initiative for all creatures in the encounter.

        Returns:
            list: All creatures sorted in initiative order where the creature
            with the highest initiative roll is at index 0.
        """
        initiative = [(c.initiative.roll()[0], c) for c in self.creatures]
        initiative.sort(key=lambda x: x[0], reverse=True)
        return initiative


if __name__ == "__main__":
    from combatsim.creature import Monster
    from combatsim.sample_creatures import simple_cleric, commoner, knight, mage
    e = Encounter([
        Monster.from_base(simple_cleric, level=5, team=1),
        Monster.from_base(commoner, level=4, team=1),
        Monster.from_base(commoner, level=4, team=1),
        Monster.from_base(knight, level=12, team=2, strength=18),
        Monster.from_base(mage, level=2, team=2)
    ])
    e.run()
