[![CI](https://github.com/Poranny/Sssnake/actions/workflows/ci.yml/badge.svg)](https://github.com/Poranny/Sssnake/actions) [![codecov](https://codecov.io/gh/Poranny/Sssnake/graph/badge.svg?token=4ZCZJ67Y1Z)](https://codecov.io/gh/Poranny/Sssnake) ![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
 ![License](https://img.shields.io/github/license/Poranny/Sssnake)

# Snake Gymnasium Environment

A highly configurable Gymnasium-based environment simulating a snake-like agent navigating a 2D space. The agent's goal is to collect candies to score points and avoid collisions (with its own growing tail, obstacles, and map boundaries).

This repository consists of two main components:

- **Core RL Environment:** Provides a custom reinforcement learning environment derived from Gymnasium API.
- **Game GUI:** Takes user input, and supplies a graphical interface built using CustomTkinter.

Action space is discrete and consists of three actions - turn left, turn right, or don't turn.

Key features include a configurable map (adjustable map size, obstacle layouts etc.), collision detection, rendering etc.


## Dependencies
- Gymnasium
- NumPy
- Pillow
- CustomTkinter (for game's GUI)

## Installation

You can install the latest test version directly from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url --upgrade https://pypi.org/simple/ "sssnake[game]"
```
Or find it at https://test.pypi.org/project/sssnake/
