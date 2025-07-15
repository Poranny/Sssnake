[![CI](https://github.com/Poranny/Sssnake/actions/workflows/ci.yml/badge.svg)](https://github.com/Poranny/Sssnake/actions) [![codecov](https://codecov.io/gh/Poranny/Sssnake/graph/badge.svg?token=4ZCZJ67Y1Z)](https://codecov.io/gh/Poranny/Sssnake) ![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
 ![License](https://img.shields.io/github/license/Poranny/Sssnake)

# Snake Gymnasium Environment

A highly configurable Gymnasium-based environment simulating a snake-like agent navigating a 2D grid. The agent's goal is to collect candies to score points, avoid collisions with its own growing tail, obstacles, and map boundaries.

This repository consists of two integrated components:

- **Core Gymnasium Environment:** Provides a pure, standalone reinforcement learning environment.
- **Interactive GUI Application:** Includes rendering capabilities, user interaction, and a graphical interface built using CustomTkinter, enabling you to play and test the environment interactively.

## Key Features

- **Configurable Map:** Adjustable map size, obstacle layouts, and candy spawn mechanics.
- **Controls:** A set of simple discrete actions (turn left, turn right, go straight).
- **Collision Detection:** Checks for collisions with tail, walls, and obstacles.
- **Rendering:** Built-in visualization for real-time gameplay and debugging.

### Dependencies
- Gymnasium
- NumPy
- Pillow
- CustomTkinter (for GUI)

## Installation

You can install the latest test version directly from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "sssnake[game]"
```
Or find it at https://test.pypi.org/project/sssnake/
