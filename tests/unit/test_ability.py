import pytest

from combatsim.ability import Ability
from combatsim.dice import Modifier

def test_add_integers_and_abilities():
    ability = Ability("Strength", 15)
    assert 5 + ability == 7
    assert ability + 5 == 7

def test_sub_integers_and_abilities():
    ability = Ability("Dexterity", 15)
    assert 5 - ability == 3
    assert ability - 1 == 1

def test_set_modifier_fails():
    ability = Ability("Constitution", 12)
    with pytest.raises(AttributeError):
        ability.mod = 5

def test_compare_abilities_with_same_mod():
    strength = Ability("Strength", 10)
    dexterity = Ability("Dexterity", 11)
    assert dexterity == strength
    assert strength == dexterity

def test_compare_abilities_with_different_mods():
    strength = Ability("Strength", 10)
    dexterity = Ability("Dexterity", 12)
    assert dexterity > strength
    assert strength < dexterity

def test_add_modifier_to_ability_returns_modifier():
    strength = Ability("Strength", 12)
    mod = Modifier(2)
    assert isinstance(strength + mod, Modifier)
    assert strength + mod == Modifier(3)

