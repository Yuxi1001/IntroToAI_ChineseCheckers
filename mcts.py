import math
import random
import copy
from board import Board

def switch_player(player):
    """
    Switch the current player.
    In your board, PLAYER_1_NR (2) and PLAYER_2_NR (3) are used.
    """
    return Board.PLAYER_2_NR if player == Board.PLAYER_1_NR else Board.PLAYER_1_NR

def simulate_move(board, move, player):
    """
    Clone the board and apply a move.
    
    Parameters:
      board: an instance of Board.
      move: a tuple (current_x, current_y, to_x, to_y).
      player: the player number making the move.
    
    Returns:
      A new board state after applying the move.
    """
    new_board = copy.deepcopy(board)
    current_x, current_y, to_x, to_y = move
    new_board.move(current_x, current_y, to_x, to_y)
    return new_board

def is_terminal(board):
    """
    Check if the board is in a terminal state.
    
    Returns:
      The winning player's number (2 or 3) if the game is over,
      or 0 if no one has won yet.
    """
    return board.is_won()

def simulate_random_playout(board, current_player, max_depth=50):
    """
    Perform a random simulation (rollout) from the current board state.
    
    The function repeatedly makes random legal moves until a terminal
    state is reached or the maximum depth is exceeded. In case max_depth
    is reached, a random winner is returned.
    
    Parameters:
      board: the current board state.
      current_player: the player whose turn it is.
      max_depth: maximum number of moves to simulate.
    
    Returns:
      The winning player's number.
    """
    depth = 0
    while True:
        winner = is_terminal(board)
        if winner != 0:
            return winner
        if depth >= max_depth:
            # When max depth is reached, return a random winner (or use a heuristic)
            return random.choice([Board.PLAYER_1_NR, Board.PLAYER_2_NR])
        legal_moves = board.get_all_legal_moves_by_player(current_player)
        if not legal_moves:
            # If no legal moves, switch player and continue
            current_player = switch_player(current_player)
            continue
        move = random.choice(legal_moves)
        board = simulate_move(board, move, current_player)
        current_player = switch_player(current_player)
        depth += 1

class MCTSNode:
    def __init__(self, board, player, move=None, parent=None):
        """
        Parameters:
          board: current board state (instance of Board).
          player: the player whose turn it is at this node.
          move: the move that led from the parent node to this node (None for root).
          parent: parent MCTSNode.
        """
        self.board = board
        self.player = player
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0       # Number of wins from simulations (from the perspective of the root player)
        self.visits = 0     # Number of times this node was visited
        # Get all legal moves for the current player at this node
        self.untried_moves = board.get_all_legal_moves_by_player(player)

    def is_fully_expanded(self):
        """Returns True if there are no untried moves left."""
        return len(self.untried_moves) == 0

    def best_child(self, c_param=math.sqrt(2)):
        """
        Select the child node with the highest UCT value.
        
        The UCT value is calculated as:
          (wins/visits) + c_param * sqrt(ln(parent.visits)/child.visits)
        
        c_param is the exploration constant.
        """
        choices = [
            (child.wins / child.visits + c_param * math.sqrt(math.log(self.visits) / child.visits), child)
            for child in self.children if child.visits > 0
        ]
        return max(choices, key=lambda x: x[0])[1] if choices else None

    def update(self, result, root_player):
        """
        Backpropagate the simulation result.
        
        If the simulation result matches the root player's number, count as a win.
        """
        self.visits += 1
        if result == root_player:
            self.wins += 1

def mcts(root_board, root_player, iterations=1000):
    """
    Perform Monte Carlo Tree Search (MCTS) from the given board state.
    
    Parameters:
      root_board: current board state (instance of Board).
      root_player: the player to move at the root node.
      iterations: the number of MCTS iterations to run.
    
    Returns:
      The best move found (tuple: current_x, current_y, to_x, to_y).
    """
    root_node = MCTSNode(root_board, root_player)

    for _ in range(iterations):
        node = root_node
        board_state = copy.deepcopy(root_board)
        current_player = root_player

        # --- Selection ---
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
            board_state = simulate_move(board_state, node.move, current_player)
            current_player = switch_player(current_player)

        # --- Expansion ---
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            board_state = simulate_move(board_state, move, current_player)
            child_node = MCTSNode(board_state, switch_player(current_player), move, node)
            node.children.append(child_node)
            node = child_node
            current_player = switch_player(current_player)

        # --- Simulation (Rollout) ---
        result = simulate_random_playout(copy.deepcopy(board_state), current_player)

        # --- Backpropagation ---
        while node is not None:
            node.update(result, root_player)
            node = node.parent

    # Choose the move from the root node that has the highest visit count
    best_child_node = max(root_node.children, key=lambda child: child.visits) if root_node.children else None
    best_move = best_child_node.move if best_child_node else None
    return best_move

if __name__ == "__main__":
    # Create the initial board state
    board = Board(players=2)
    # Assume PLAYER_1_NR (2) starts the game
    root_player = Board.PLAYER_1_NR

    # Run MCTS to select the best move for the root player
    best_move = mcts(board, root_player, iterations=1000)
    print("MCTS selected move:", best_move)
