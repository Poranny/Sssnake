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
