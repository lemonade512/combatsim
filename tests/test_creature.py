import unittest

from combatsim.creature import Ability, Creature, Monster, RulesError
from combatsim.spells import Spell


class DummySpell(Spell):
    min_level = 1

    def cast(self):
        pass


class TestCreature(unittest.TestCase):

    def test_ability_modifiers_computed_from_abilties(self):
        creature = Creature(
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
        creature = Creature(max_hp=5)
        creature.hp -= 1
        creature.heal(5000)
        self.assertEqual(creature.hp, creature.max_hp)

    def test_cast_spell_depletes_spell_slot(self):
        creature = Creature(spell_slots=[1], spells=[DummySpell])
        creature.cast(DummySpell, 1)
        self.assertEqual(creature.spell_slots[0], 0)

    def test_cast_spell_without_spell_slot_raises_error(self):
        creature = Creature(spells=[DummySpell])
        self.assertRaises(RulesError, creature.cast, DummySpell, 1)

    def test_cast_too_many_spells_raises_error(self):
        creature = Creature(spell_slots=[1], spells=[DummySpell])
        creature.cast(DummySpell, 1)
        self.assertRaises(RulesError, creature.cast, DummySpell, 1)

    def test_cast_spell_not_in_creature_spell_list_raises_error(self):
        creature = Creature(spell_slots=[1], spells=[])
        self.assertRaises(RulesError, creature.cast, DummySpell, 1)


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
