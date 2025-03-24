import math
import copy
import random
import numpy as np
from board import Board

# Configuration parameters
C_PUCT = 1.0
MCTS_SIMULATIONS = 800
TREE_TAU = 1.0
EPSILON = 1e-8
REWARD = {'win': 1.0}

# A simple move encoding (for demonstration only; it does not affect the search)
def encode_move(move):
    return hash(move) % 100000

# Node class: stores the board state and the current player, and the edges from this node
class Node:
    def __init__(self, state, currPlayer):
        self.state = state
        self.currPlayer = currPlayer
        self.edges = []  # All edges expanded from this node
        # Optional: dictionary to store move probabilities (not used in pure MCTS)
        self.pi = {}

    def isLeaf(self):
        return len(self.edges) == 0

# Edge class: connects a parent node to a child node and records the move and statistics
class Edge:
    def __init__(self, inNode, outNode, prior, fromPos, toPos):
        self.inNode = inNode
        self.outNode = outNode
        self.currPlayer = inNode.currPlayer
        self.fromPos = fromPos      # Starting coordinates (e.g., (x, y))
        self.toPos = toPos          # Destination coordinates (e.g., (x, y))
        self.stats = {
            'N': 0,      # Visit count
            'W': 0,      # Total simulation value
            'Q': 0,      # Average value
            'P': prior   # Prior probability (set to 1 for pure MCTS)
        }

# Simulate a random playout (rollout) until a terminal state is reached.
# If max_depth is reached, a random winner is chosen.
def simulate_random_playout(state, current_player, max_depth=50):
    depth = 0
    while True:
        winner = state.is_won()
        if winner:
            return winner
        if depth >= max_depth:
            return random.choice([Board.PLAYER_1_NR, Board.PLAYER_2_NR])
        legal_moves = state.get_all_legal_moves_by_player(current_player)
        if not legal_moves:
            current_player = Board.PLAYER_1_NR if current_player == Board.PLAYER_2_NR else Board.PLAYER_2_NR
            continue
        move = random.choice(legal_moves)
        x, y, to_x, to_y = move
        state.move(x, y, to_x, to_y)
        current_player = Board.PLAYER_1_NR if current_player == Board.PLAYER_2_NR else Board.PLAYER_2_NR
        depth += 1

# Pure MCTS class
class MCTS:
    def __init__(self, root, cpuct=C_PUCT, num_itr=MCTS_SIMULATIONS, tree_tau=TREE_TAU):
        self.root = root
        self.cpuct = cpuct
        self.num_itr = num_itr
        self.tree_tau = tree_tau

    # Selection phase: traverse the tree from the root until a leaf node is reached.
    def moveToLeaf(self):
        breadcrumbs = []
        currentNode = self.root

        while not currentNode.isLeaf():
            N_sum = sum(edge.stats['N'] for edge in currentNode.edges)
            maxQU = float('-inf')
            chosen_edges = []
            for edge in currentNode.edges:
                U = self.cpuct * edge.stats['P'] * math.sqrt(N_sum) / (1.0 + edge.stats['N'])
                QU = edge.stats['Q'] + U
                if QU > maxQU:
                    maxQU = QU
                    chosen_edges = [edge]
                elif abs(QU - maxQU) < EPSILON:
                    chosen_edges.append(edge)
            chosen_edge = random.choice(chosen_edges)
            breadcrumbs.append(chosen_edge)
            currentNode = chosen_edge.outNode
        return currentNode, breadcrumbs

    # Expansion and Backpropagation phase: if the leaf is non-terminal, expand a child and run a simulation.
    def expandAndBackUp(self, leafNode, breadcrumbs):
        winner = leafNode.state.is_won()
        if winner:
            # Terminal state: backpropagate the result immediately.
            for edge in breadcrumbs:
                direction = 1 if edge.currPlayer == winner else -1
                edge.stats['N'] += 1
                edge.stats['W'] += REWARD['win'] * direction
                edge.stats['Q'] = edge.stats['W'] / edge.stats['N']
            return

        legal_moves = leafNode.state.get_all_legal_moves_by_player(leafNode.currPlayer)
        if not legal_moves:
            # If no legal moves, treat as a loss for the current player.
            for edge in breadcrumbs:
                edge.stats['N'] += 1
                edge.stats['W'] += -REWARD['win']
                edge.stats['Q'] = edge.stats['W'] / edge.stats['N']
            return

        # Randomly select a move for expansion.
        move = random.choice(legal_moves)
        x, y, to_x, to_y = move
        new_state = copy.deepcopy(leafNode.state)
        new_state.move(x, y, to_x, to_y)
        next_player = Board.PLAYER_1_NR if leafNode.currPlayer == Board.PLAYER_2_NR else Board.PLAYER_2_NR
        newNode = Node(new_state, next_player)
        newEdge = Edge(leafNode, newNode, prior=1.0, fromPos=(x, y), toPos=(to_x, to_y))
        leafNode.edges.append(newEdge)

        # Run a random simulation from the newly expanded node.
        simulation_state = new_state.fast_copy()
        simulation_result = simulate_random_playout(simulation_state, newNode.currPlayer)
        # From the perspective of the leafNode's current player: win = 1, loss = -1.
        value = 1 if simulation_result == leafNode.currPlayer else -1

        # Update the new edge with the simulation result.
        newEdge.stats['N'] += 1
        newEdge.stats['W'] += value
        newEdge.stats['Q'] = newEdge.stats['W'] / newEdge.stats['N']

        # Backpropagate the simulation result along the entire path.
        for edge in breadcrumbs:
            direction = 1 if edge.currPlayer == leafNode.currPlayer else -1
            edge.stats['N'] += 1
            edge.stats['W'] += value * direction
            edge.stats['Q'] = edge.stats['W'] / edge.stats['N']

    # The overall search process: perform multiple iterations of selection, expansion, simulation, and backpropagation.
    def search(self):
        for i in range(self.num_itr):
            leafNode, breadcrumbs = self.moveToLeaf()
            self.expandAndBackUp(leafNode, breadcrumbs)
        # Choose the edge with the highest visit count from the root as the best move.
        best_edge = max(self.root.edges, key=lambda e: e.stats['N']) if self.root.edges else None
        return best_edge

# External interface: call mcts_search to get the best move (format: (x, y, to_x, to_y))
def mcts_search(root_board, root_player, iterations=MCTS_SIMULATIONS):
    root = Node(root_board, root_player)
    tree = MCTS(root, num_itr=iterations)
    best_edge = tree.search()
    if best_edge is None:
        return None
    return (best_edge.fromPos[0], best_edge.fromPos[1], best_edge.toPos[0], best_edge.toPos[1])

if __name__ == '__main__':
    board_instance = Board()
    best_move = mcts_search(board_instance, Board.PLAYER_1_NR, iterations=1000)
    print("MCTS selected move:", best_move)
