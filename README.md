# ScotlandYardAI

ScotlandYardAI is a Python-based implementation of the variant of the classic board game *Scotland Yard*. This project includes AI algorithms to simulate both the detectives and Mr. X, providing an engaging and strategic gameplay experience.
In this variant of the game, there are only three modes of transportation: taxi, bus and underground subway. 
Mr.X is played by humans while the detectives are played by the computer. There are two AI algorithms to simulate the movement of the detectives.
- **Heuristic-Based Greedy Approach**: Relies primarily on heuristics to evaluate moves:
    - Proximity: Moves closer to possible Mr. X locations are prioritized.
    - Coverage: Penalizes moves overlapping with other detectives to ensure better board coverage.
    - Immediate Evaluation: Each move is scored on the basis of the current situation without a deep look-ahead.
- **Bayesian + Alpha-Beta Pruning Approach**:Incorporates probabilistic reasoning and strategic look-ahead:
    - Bayesian Probabilities: Calculates likelihoods for Mr. X's location based on historical movements, distances, and escape routes.
    - Alpha-Beta Pruning: Conducts a depth-limited mini-max search to evaluate not just the immediate impact of moves but also their future implications.
    - Complex Scoring: Combines immediate evaluation and probabilistic reasoning with predictions of future states.
    
## Features

- **Game Engine:** Implements the core mechanics of the Scotland Yard game.
- **AI for Players:** Heuristics and decision-making algorithms for both Mr. X and detectives.
- **Graph-Based Representation:** Models the board as a graph for efficient movement and decision-making.
- **GUI Support:** Visual representation of the game board and player movements.
- **Customizable:** Allows players to configure starting locations, heuristics, and game settings.

## Repository Structure

- `main.py`: Entry point for running the game.
- `board.py`: Handles the game board representation and logic.
- `detectives.py`: Implements the logic for detective players.
- `mrx.py`: Implements the logic for Mr. X.
- `heuristic.py`: Contains heuristics for AI decision-making.
- `gui.py`: Provides a graphical interface for the game.
- `path.py`: Displays a graph showing the entire board game in a simple NetworkX graph.
- `engine/`: Contains the core game engine logic.
  - `game.py`: Manages the game state and flow.
  - `player.py`: Defines player attributes and behaviors.
- `board_data.txt`: Stores data for the game board structure.
- `node_locations.txt`: Defines the locations of nodes on the game board.
- `start_locations.txt`: Specifies the initial positions of players.
- `fullgamegraph.py`: Models the entire game graph for analysis and AI planning.
- `board.jpg`: An image of the game board for reference or GUI use.

## Usage

1. Clone the repository:
    ```bash
    git clone https://github.com/Sky-Lance/ScotlandYardAI
    cd ScotlandYardAI
    ```

2. Install all requirements:
    ```bash
    pip install -r requirements.txt
    ```
  
3. Run the game! (and view the simulation)
    ```bash
    python main.py
    ```

If you wish to control Mr. X, make sure to change the `player` variable in `mrx.py` to anything other than random. 
