import unittest

from combatsim.creature import Ability, Creature, Monster


class TestCreature(unittest.TestCase):

    def test_ability_modifiers_computed_from_abilties(self):
        creature = Monster(
            strength=4,
            dexterity=5,
            constitution=6,
            intelligence=15,
            wisdom=16,
            charisma=22
        )
        self.assertEqual(creature.strength.mod, -3)
        self.assertEqual(creature.dexterity.mod, -3)
        self.assertEqual(creature.constitution.mod, -2)
        self.assertEqual(creature.intelligence.mod, 2)
        self.assertEqual(creature.wisdom.mod, 3)
        self.assertEqual(creature.charisma.mod, 6)

    def test_max_heal_for_creature(self):
        creature = Monster()
        creature.hp -= 1
        creature.heal(5000)
        self.assertEqual(creature.hp, creature.max_hp)


class TestAbility(unittest.TestCase):

    def test_add_integers_and_abilities(self):
        ability = Ability("Strength", 15)
        self.assertEqual(5 + ability, 7)
        self.assertEqual(ability + 5, 7)

    def test_sub_integers_and_abilities(self):
        ability = Ability("Dexterity", 15)
        self.assertEqual(5 - ability, 3)
        self.assertEqual(ability - 1, 1)

    def test_set_modifier_fails(self):
        ability = Ability("Constitution", 12)
        def _assign():
            ability.mod = 5
        self.assertRaises(AttributeError, _assign)
