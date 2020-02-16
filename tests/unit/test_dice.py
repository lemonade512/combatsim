import pytest
import unittest

from combatsim.dice import Dice, Modifier


@pytest.mark.parametrize("dice,result", [
    (Dice("d1"), [1]),
    (Dice(["d1", "d1"]), [1, 1]),
    (Dice(["5d1"]), [5]),
    (Dice("d1") + Modifier(1), [2]),
    (Dice(["2d1", "d1"]) + Modifier(1), [3, 2]),
    (Dice(["1d1"]) + Modifier(1) + Modifier(2), [4]),
    (Dice([]), [])
])
def test_roll_d1s(dice, result):
    assert dice.roll() == result

@pytest.mark.parametrize("dice,average", [
    (Dice("d6"), 3.5),
    (Dice("d6") + Modifier(1), 4.5),
    (Dice(["2d6", "2d8"]), 16),
    (Dice(["1d6", "1d8"]) + Modifier(1), 10)
])
def test_dice_averages(dice, average):
    assert dice.average == average

@pytest.mark.parametrize("dice,expected", [
    (Dice("1d20"), 20),
    (Dice(["1d20", "2d20"]), 60),
    (Dice(["1d20", "1d10"]) + Modifier(5), 40)
])
def test_dice_maxes(dice, expected):
    assert dice.max == expected

@pytest.mark.parametrize("dice,multiple,expected", [
    (Dice("1d20"), 2, Dice(["1d20", "1d20"])),
    (Dice("1d20") + Modifier(2), 2, Dice(["1d20", "1d20"]) + Modifier(2)),
    (Dice("1d20"), 0, Dice([]))
])
def test_dice_multiples(dice, multiple, expected):
    assert dice * multiple == expected

def test_add_dynamic_modifiers_to_dice():
    modifier = Modifier(1)
    dice = Dice("d1") + modifier
    assert dice.roll() == [2]
    modifier.mod = 2
    assert dice.roll() == [3]

def test_add_int():
    dice = Dice("1d20") + 1
    assert dice == Dice("1d20") + Modifier(1)

def test_sub_int():
    dice = Dice("1d20") - 1
    assert dice == Dice("1d20") + Modifier(-1)
