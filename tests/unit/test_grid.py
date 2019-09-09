import unittest

from combatsim.grid import Grid


class TestGrid(unittest.TestCase):

    def test_simple_grid_creation(self):
        grid = Grid(1,1)
        self.assertEqual(grid.width, 1)
        self.assertEqual(grid.height, 1)
        self.assertEqual(grid[0,0], None)

    def test_grid_set_and_get_item(self):
        grid = Grid(1,1)
        grid[0,0] = 1
        self.assertEqual(grid[0,0], 1)

    def test_grid_set_single_item(self):
        grid = Grid(1,2)
        grid[0,0] = 1
        self.assertEqual(grid[0,0], 1)
        self.assertEqual(grid[0,1], None)

    def test_grid_with_invalid_height_raises_exception(self):
        self.assertRaises(ValueError, Grid, 10, 0)

    def test_grid_with_invalid_width_raises_exception(self):
        self.assertRaises(ValueError, Grid, 0, 10)

    def test_grid_set_item_invalid_x_raises_exception(self):
        grid = Grid(1,1)
        self.assertRaises(IndexError, grid.__setitem__, (1,0), None)

    def test_grid_set_item_invalid_y_raises_exception(self):
        grid = Grid(1,1)
        self.assertRaises(IndexError, grid.__setitem__, (0,1), None)

    def test_grid_get_item_invalid_x_raises_exception(self):
        grid = Grid(1,1)
        self.assertRaises(IndexError, grid.__getitem__, (1,0))

    def test_grid_get_item_invalid_y_raises_exception(self):
        grid = Grid(1,1)
        self.assertRaises(IndexError, grid.__getitem__, (0,1))
