from collections import defaultdict

from combatsim.dice import Dice
from combatsim.tactics import Healer
from combatsim.spells import CureWounds

class Encounter:

    def __init__(self, creatures):
        self.creatures = creatures

    def run(self):
        print("==== Combatants ====")
        for creature in self.creatures:
            print(f"{creature}: {creature.hp}")

        print("\n==== BEGIN ENCOUNTER ====")
        initiative = self.roll_initiative()
        i = 0
        while True:
            current_creature = initiative[i][1]
            current_creature.tactics.act([c for c in self.creatures if c != current_creature])
            if self.encounter_over():
                break
            i = (i + 1) % len(initiative)

        print("\n==== END ENCOUNTER ====")
        for creature in self.creatures:
            print(f"\t{creature}: {creature.hp}")

    def encounter_over(self):
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
    from combatsim.weapon import Weapon
    longsword = Weapon("Longsword", "strength", Dice("1d8"), "slashing")
    fists = Weapon("Fists", "strength", Dice("1d4"), "bludgeoning")
    #e = Encounter([
    #    Monster(name="Fast Man", strength=12, dexterity=25, attacks=[longsword], team="a"),
    #    Monster(name="Beefcake", strength=18, attacks=[fists], team="a"),
    #    Monster(name="Commoner 2", attacks=[fists], team="a", resistances=["slashing", "piercing"]),
    #    Monster(name="Knight", strength=14, dexterity=14, attacks=[longsword], ac=18)
    #])
    e = Encounter([
        Monster(
            name="Healer", attacks=[fists], spell_slots=[3],
            spells=[CureWounds], level=5, tactics=Healer, team=1
        ),
        Monster(name="Commoner", attacks=[fists], resistances=["slashing"], level=5, team=1),
        Monster(name="Knight", strength=14, attacks=[longsword], ac=14, level=5)
    ])
    e.run()
