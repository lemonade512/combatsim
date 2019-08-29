""" Manages grid for combat. """


class Grid:

    def __init__(self, width, height):
        self._grid = [
            [None] * width
        ] * height
