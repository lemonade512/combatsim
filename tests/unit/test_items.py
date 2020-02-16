import unittest
from unittest.mock import patch

from combatsim.items import Armor, Weapon
from combatsim.creature import Monster
from combatsim.dice import Dice


def test_armor_with_no_max_dex(monster):
    monster.dexterity.value = 20
    armor = Armor("Test", 12, owner=monster)
    assert armor.ac == 17

@patch("combatsim.dice.random.randint")
def test_attack_with_advantage_returns_max(randint, monster):
    randint.side_effect = [1, 20]
    attack = Weapon("test", None, None, owner=monster)
    assert attack.attack_roll(advantage=True)[0] == 20

@patch("combatsim.dice.random.randint")
def test_attack_with_disadvantage_returns_min(randint, monster):
    randint.side_effect = [1, 20]
    attack = Weapon("test", None, None, owner=monster)
    assert attack.attack_roll(disadvantage=True)[0] == 1

@patch("combatsim.dice.random.randint")
def test_attack_returns_single_value(randint, monster):
    randint.side_effect = [5, 15]
    attack = Weapon("test", None, None, owner=monster)
    assert attack.attack_roll()[0] == 5

@patch("combatsim.dice.random.randint")
def test_attack_with_finess_uses_max_of_strength_and_dex(randint):
    randint.return_value = 5
    strong_monster = Monster(strength=18)
    attack = Weapon("test", None, None, owner=strong_monster, properties=["finesse"])
    assert attack.attack_roll()[0] == 9
    fast_monster = Monster(dexterity=18)
    attack.owner = fast_monster
    assert attack.attack_roll()[0] == 9

@patch("combatsim.dice.random.randint")
def test_melee_attack_uses_strength(randint, monster):
    randint.return_value = 1
    monster.strength.value = 18
    attack = Weapon("test", None, None, melee=True, owner=monster)
    assert attack.attack_roll()[0] == 5

@patch("combatsim.dice.random.randint")
def test_ranged_attack_uses_dexterity(randint, monster):
    randint.return_value = 1
    monster.dexterity.value = 18
    attack = Weapon("test", None, None, melee=False, owner=monster)
    assert attack.attack_roll()[0] == 5

@patch("combatsim.dice.random.randint")
def test_advantage_disadvantage_cancel_out(randint, monster):
    randint.side_effect = [1, 20]
    attack = Weapon("test", None, None, owner=monster)
    assert attack.attack_roll(advantage=True, disadvantage=True)[0] == 1
    assert attack.attack_roll(advantage=True, disadvantage=True)[0] == 20

@patch("combatsim.dice.random.randint")
def test_crit_is_returned_on_nat_20(randint, monster):
    randint.return_value = 20
    attack = Weapon("test", None, None, owner=monster)
    assert attack.attack_roll()[1]

@patch("combatsim.dice.random.randint")
def test_crit_not_returned_on_modified_20(randint, monster):
    randint.return_value = 19
    monster.strength.value = 12
    attack = Weapon("test", None, None, owner=monster)
    roll, crit = attack.attack_roll()
    assert roll == 20
    assert not crit

@patch("combatsim.dice.random.randint")
def test_attack_mod_overrides_strength(randint, monster):
    randint.return_value = 5
    weapon = Weapon("test", None, None, attack_mod=5, owner=monster)
    roll, crit = weapon.attack_roll()
    assert roll == 10

@patch("combatsim.dice.random.randint")
def test_damage_mod_overrides_strength(randint, monster):
    randint.return_value = 5
    weapon = Weapon(
        "test", Dice("1d1"), None, damage_mod=5, owner=monster
    )
    roll, _ = weapon.damage_roll()
    assert roll == 10
