from dice import Dice

class Encounter:

    def __init__(self, creatures):
        self.creatures = creatures

    def run(self):
        initiative = self.roll_initiative()
        i = 0
        while True:
            current_creature = initiative[i][1]
            current_creature.act([c for c in self.creatures if c != current_creature])
            if self.encounter_over():
                break
            i = (i + 1) % len(initiative)

        for creature in self.creatures:
            print(f"{creature}: {creature.hp}")

    def encounter_over(self):
        alive = 0
        for creature in self.creatures:
            if creature.hp > 0:
                alive += 1

        return alive <= 1

    def roll_initiative(self):
        """ Rolls initiative for all creatures in the encounter.

        Returns:
            list: All creatures sorted in initiative order where the creature
            with the highest initiative roll is at index 0.
        """
        initiative = []
        for creature in self.creatures:
            roll = Dice.roll('1d20') + creature.dexterity
            initiative.append((roll, creature))

        initiative.sort(key=lambda x: x[0], reverse=True)
        return initiative


if __name__ == "__main__":
    from creature import Creature
    e = Encounter([
        Creature(name="Fast Man", dexterity=25),
        Creature(name="Commoner 1"),
        Creature(name="Commoner 2")
    ])
    e.run()
