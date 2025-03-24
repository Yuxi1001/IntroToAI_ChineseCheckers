# MCTS Chinese Checkers Game

This project is a Python implementation of a Chinese Checkers game with an AI opponent powered by a pure Monte Carlo Tree Search (MCTS) algorithm. The project uses Pygame for the graphical interface and provides custom logic to prevent the AI from moving backward.

## Features

- **Chinese Checkers Board:**  
  The board is set up with initial positions for two players. Red is human player and AI controls the blue one. The board layout is generated dynamically.

- **MCTS AI:**  
  The AI opponent uses a pure MCTS algorithm with multiple iterations of selection, expansion, simulation, and backpropagation to decide on moves.

- **Pygame Interface:**  
  The game features a graphical interface built with Pygame. Human players can select and move pieces using the mouse, and press **Enter** to confirm moves when needed (mostly when you choose to jump).

## File Structure

- **`board.py`**  
  Contains the `Board` class that manages the board layout, legal moves, move execution, and win conditions. It now includes a filtering mechanism to prevent backward moves.

- **`mcts.py`**  
  Implements the MCTS algorithm, including Node and Edge classes, rollouts, and the overall search process.

- **`game.py`**  
  Manages the game loop and user interface using Pygame. It handles user inputs, draws the board and pieces, and integrates the AI move logic.

## Requirements

- Python 3.x
- [Pygame](https://www.pygame.org/)  
  Install via pip: `pip install pygame`
- [Numpy](https://numpy.org/)  
  Install via pip: `pip install numpy`

## Usage

To start the game, navigate to the project directory and run game.py with Python using the following command:
```bash
python game.py

