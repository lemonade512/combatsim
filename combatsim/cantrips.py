""" Defines all cantrips available in D&D.

Note: I will only define cantrips that are combat spells. I cannot simulate
creative uses of spells such as using prestidigitation to scare a monster.
Therefore, I will be focussing on things that do damage, or exert some
positive or negative effects on nearby creatures.
"""

# Acid Splash: You hurl a bubble of acid.
#
# Choose one or two creatures you can see within range. If you choose two, they
# must be within 5 feet of each other. A target must succeed on a Dexterity
# saving throw or take 1d6 acid damage.
#
# This spell’s damage increases by 1d6 when you reach 5th level (2d6), 11th level
# (3d6), and 17th level (4d6).
acid_splash = Spell(
  casting_time="action",
  targets=Sphere(radius=5, max_=2, filter_="enemies"),
  range_=60,
  components={"V", "S"},
  effects=[
    SavingThrow(
      "dexterity",
      CantripDamage(Dice("1d6"), "acid"),
      save_multiplier=0
    )
  ],
  school="conjuration"
)


# Blade Ward: You extend your hand and trace a sigil of warding in the air.
#
# Until the end of your next turn, you have resistance against bludgeoning,
# piercing, and slashing damage dealt by weapon attacks.
blade_ward = Spell(
  casting_time="action",
  targets=Sphere(radius=0),
  range_=0,
  components={"V", "S"},
  effects=[
    Resistance(['bludgeoning', 'piercing', 'slashing'], duration=1)
  ],
  school="abjuration"
)

# Booming Blade
#
# As part of the action used to cast this spell, you must make a melee attack
# with a weapon against one creature within the spell’s range, otherwise the
# spell fails. On a hit, the target suffers the attack’s normal effects, and it
# becomes sheathed in booming energy until the start of your next turn. If the
# target willingly moves before then, it immediately takes 1d8 thunder damage,
# and the spell ends.
#
# This spell’s damage increases when you reach higher levels. At 5th level, the
# melee attack deals an extra 1d8 thunder damage to the target, and the damage
# the target takes for moving increases to 2d8. Both damage rolls increase by
# 1d8 at 11th level and 17th level.
booming_blade = Spell(
    casting_time="action",
    targets=Sphere(radius=0, max_=1),
    range_=5,
    components={"V", "M"},
    effects=[
        MeleeAttack(  # Caster makes a melee attack
            on_hit=[Marked(
                CantripDamage(Dice("1d8"), "thunder"),
                on="WillingMovement",   # Event name
                duration=1,
                ends_on_activation=True
            )]
        )
    ],
    school="evocation"
)

# You create a ghostly, skeletal hand in the space of a creature within range.
# Make a ranged spell attack against the creature to assail it with the chill
# of the grave. On a hit, the target takes 1d8 necrotic damage, and it can't
# regain hit points until the start of your next turn. Until then, the hand
# clings to the target.
#
# If you hit an undead target, it also has disadvantage on attack rolls against
# you until the end of your next turn.
#
# This spell's damage increases by 1d8 when you reach 5th level (2d8), 11th
# level (3d8), and 17th level (4d8).
chill_touch = Spell(
    casting_time="action",
    targets=Sphere(radius=0, max_=1),
    range_=120,
    components={"V", "S"},
    effects=[
        RangedSpellAttack(  # Caster makes a ranged spell attack
            on_hit=[
                CantripDamage(Dice("1d8", "necrotic")),
                BlockHealing(duration=1),
                Filtered(Disadvantage("attacks on caster"), type_="undead")
            ]
        ),
    ],
    school="necromancy"
)
