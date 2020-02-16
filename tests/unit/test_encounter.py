from combatsim.dice import Dice, Modifier
from combatsim.creature import Monster
from combatsim.encounter import Encounter


def test_initiative_order():
    medium = Monster(name="med", initiative=Dice("d1") + Modifier(3))
    fast = Monster(name="fast", initiative=Dice("d1") + Modifier(5))
    slow = Monster(name="slow", initiative=Dice("d1"))
    encounter = Encounter([medium, fast, slow])
    assert encounter.roll_initiative()[0][1].name == fast.name
