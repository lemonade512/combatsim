""" Manages grid for combat. """


class Grid:

    def __init__(self, width, height):
        if width <= 0:
            raise ValueError(f"{width} is not a valid width")
        if height <= 0:
            raise ValueError(f"{height} is not a valid height")

        self.width = width
        self.height = height
        self._grid = [
            [None] * width
        ] * height

    def __getitem__(self, position):
        x,y = position
        if x >= self.width or x < 0:
            raise IndexError(f"X value of {x} not within [0,{self.width})")
        if y >= self.height or y < 0:
            raise IndexError(f"Y value of {y} not within [0,{self.height})")
        return self._grid[x][y]

    def __setitem__(self, position, val):
        """ Expects an (x,y) position to set. """
        x,y = position
        if x >= self.width or x < 0:
            raise IndexError(f"X value of {x} not within [0,{self.width})")
        if y >= self.height or y < 0:
            raise IndexError(f"Y value of {y} not within [0,{self.height})")
        if self._grid[x][y] is not None:
            raise
        self._grid[x][y] = val
