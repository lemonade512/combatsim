import pytest

from combatsim.grid import Grid

@pytest.mark.parametrize("width,height", [(0,10), (10,0), (-1,10), (10,-1)])
def test_grid_with_invalid_height_raises_exception(width, height):
    with pytest.raises(ValueError):
        Grid(width, height)

@pytest.mark.parametrize("x,y", [(10,0), (0,10), (-1,0), (0,-1)])
def test_grid_get_invalid_coords_raises_exception(x,y):
    grid = Grid(5,5)
    with pytest.raises(IndexError):
        _ = grid[x,y]

@pytest.mark.parametrize("x,y", [(10,0), (0,10), (-1,0), (0,-1)])
def test_grid_set_invalid_coords_raises_exception(x,y):
    grid = Grid(5,5)
    with pytest.raises(IndexError):
        grid[x,y] = None

def test_simple_grid_creation():
    grid = Grid(1,1)
    assert grid.width == 1
    assert grid.height == 1
    assert grid[0,0] == None

def test_grid_set_and_get_item():
    grid = Grid(1,1)
    grid[0,0] = 1
    assert grid[0,0] == 1

def test_grid_set_single_item():
    grid = Grid(1,2)
    grid[0,0] = 1
    assert grid[0,0] == 1
    assert grid[0,1] == None
