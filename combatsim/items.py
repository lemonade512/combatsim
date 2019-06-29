
# TODO (phillip): When equipping an item, consider the following:
#   * What happens when you have two items that give the same effect, and one is un-equipped
#   * What happens when dual wielding the same type of weapon

class Item:

    def __init__(self, name):
        self.name = name


class Armor(Item):

    def __init__(self, name, base_ac, max_dex):
        super().__init__(name)
        self.base_ac = base_ac
        self.max_dex = max_dex
