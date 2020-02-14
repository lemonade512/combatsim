Inspired by https://github.com/matteoferla/DnD-battler/blob/master/DnD.py

The goal of this project is to provide a rough simulator for designing balance
encounters for the 5th edition of Dungeons & Dragons. There are other
simulators that exist, but most of them ignore a majority of the spells
available to the player, and they don't take into account the tactics of
grid-based combat.

Written in Python 3

## Getting Started
First, setup your environment using pyenv and poetry:
```
cd /path/to/combatsim
pyenv install 3.8.1
poetry install
```
If you have a problem running the above, you may need to run `pyenv local 3.8.1`.

Next, make sure you can run all the unit and functional tests:
```
poetry shell
pytest tests
```
