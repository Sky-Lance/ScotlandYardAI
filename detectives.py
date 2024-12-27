# 1. Imports and Configuration
import networkx as nx
from engine.player import Player
from engine import boardmap
from typing import List, Tuple, Set, Dict
import random
from path import visualize_traversal_path
from functools import lru_cache
import math

# Game Constants
turn = 1
agent = 0
reveal_turns = [3, 8, 13, 18, 24]
MAX_DEPTH = 2
INFINITY = float('inf')

# 2. Helper Functions and Caching
@lru_cache(maxsize=1024)
def get_valid_transport_moves(pos: int, transport_type: str) -> Set[int]:
    """Get valid moves for a transport type from a position"""
    return set(boardmap[pos].get(transport_type, []))

@lru_cache(maxsize=1024)
def get_shortest_path_length(pos1: int, pos2: int) -> int:
    """Get cached shortest path length between two positions"""
    try:
        return len(nx.shortest_path(nx.Graph(boardmap), pos1, pos2)) - 1
    except nx.NetworkXNoPath:
        return INFINITY

def get_possible_locations(x_history: List[Tuple[int, str]], last_known_pos: int, moves_since_reveal: int) -> Set[int]:
    """Track possible Mr. X locations"""
    possible_nodes = {last_known_pos}
    
    for _, transport in x_history[-moves_since_reveal:]:
        next_possible = set()
        for node in possible_nodes:
            if transport in boardmap[node]:
                next_possible.update(boardmap[node][transport])
        possible_nodes = next_possible
    
    return possible_nodes

# 3. Probability Calculations
def calculate_probability(node: int, possible_nodes: Set[int], detectives: List[Player], x_history: List[Tuple[int, str]]) -> float:
    """Calculate Bayesian probability for Mr. X location"""
    if node not in possible_nodes:
        return 0.0
    
    prior = 1.0 / len(possible_nodes)
    likelihood = 1.0
    
    # Distance factor
    min_detective_distance = min(get_shortest_path_length(d.pos, node) for d in detectives)
    likelihood *= (1.0 + min_detective_distance / 5.0)
    
    # Escape routes factor
    escape_routes = sum(1 for t in ['taxi', 'bus', 'underground'] 
                       if t in boardmap[node] and boardmap[node][t])
    likelihood *= (1.0 + escape_routes / 3.0)
    
    # Historical movement pattern factor
    if x_history:
        recent_transports = [t for _, t in x_history[-3:]]
        transport_variety = len(set(recent_transports))
        likelihood *= (1.0 + transport_variety / 3.0)
    
    return prior * likelihood

def print_node_probabilities(possible_nodes: Set[int], detectives: List[Player], x_history: List[Tuple[int, str]]) -> Dict[int, float]:
    """Calculate and print node probabilities"""
    probabilities = {}
    total_likelihood = 0
    
    for node in possible_nodes:
        prob = calculate_probability(node, possible_nodes, detectives, x_history)
        probabilities[node] = prob
        total_likelihood += prob
    
    if total_likelihood > 0:
        for node in probabilities:
            probabilities[node] /= total_likelihood
    
    sorted_nodes = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 10 most likely Mr. X locations:")
    print("Node  |  Probability")
    print("-" * 20)
    for node, prob in sorted_nodes[:10]:
        print(f"{node:4d}  |  {prob:.3f}")
    
    return probabilities

# 4. Move Evaluation
def get_valid_moves(detective: Player, detectives: List[Player]) -> List[Tuple[int, str]]:
    """Get all valid moves for a detective"""
    valid_moves = []
    detective_positions = {d.pos for d in detectives}
    
    for transport, count in detective.tickets.items():
        if count <= 0 or transport in ['black', '2x']:
            continue
        
        if transport in boardmap[detective.pos]:
            for next_pos in boardmap[detective.pos][transport]:
                if next_pos not in detective_positions:
                    valid_moves.append((next_pos, transport))
    
    return valid_moves

def evaluate_position(pos: int, detectives: List[Player], possible_x_locations: Set[int], x_history: List[Tuple[int, str]]) -> float:
    """Evaluate a position's strategic value"""
    if not possible_x_locations:
        return 0.0
    
    score = 0.0
    detective_positions = {d.pos for d in detectives}
    
    for x_pos in possible_x_locations:
        prob = calculate_probability(x_pos, possible_x_locations, detectives, x_history)
        
        # Distance factor
        distance = get_shortest_path_length(pos, x_pos)
        position_score = prob * (10.0 / (1.0 + distance))
        
        # Coverage factor
        coverage = len(set().union(*[set(boardmap[pos].get(t, [])) 
                                   for t in ['taxi', 'bus', 'underground']]))
        position_score *= (1.0 + coverage / 20.0)
        
        # Team coordination factor
        if any(get_shortest_path_length(d_pos, x_pos) <= 2 
               for d_pos in detective_positions if d_pos != pos):
            position_score *= 1.5
        
        score += position_score
    
    return score

# 5. Alpha-Beta Search
def alpha_beta_search(detective: Player, depth: int, alpha: float, beta: float, 
                     maximizing: bool, possible_nodes: Set[int], 
                     detectives: List[Player], valid_moves: List[Tuple[int, str]], 
                     x_history: List[Tuple[int, str]]) -> Tuple[float, Tuple[int, str]]:
    """Alpha-beta pruning search with immediate and future evaluation"""
    
    if depth == 0 or not valid_moves:
        score = evaluate_position(detective.pos, detectives, possible_nodes, x_history)
        return score, None
    
    if maximizing:
        max_eval = -INFINITY
        best_move = None
        
        for move in valid_moves:
            new_pos, transport = move
            
            # Create new detective state
            new_tickets = detective.tickets.copy()
            new_tickets[transport] -= 1
            new_detective = Player(new_tickets, new_pos, detective.name)
            
            # Update detectives list with new position
            new_detectives = [new_detective if d.name == detective.name else d for d in detectives]
            
            # Calculate immediate score
            immediate_score = evaluate_position(new_pos, new_detectives, possible_nodes, x_history)
            
            # Look ahead for future score
            future_score, _ = alpha_beta_search(
                new_detective, depth - 1, alpha, beta, False,
                possible_nodes, new_detectives, valid_moves, x_history
            )
            
            # Combine scores with more weight on immediate moves
            eval_score = (0.7 * immediate_score) + (0.3 * future_score)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
                
        return max_eval, best_move
    
    else:
        min_eval = INFINITY
        best_move = None
        
        for move in valid_moves:
            new_pos, transport = move
            
            new_tickets = detective.tickets.copy()
            new_tickets[transport] -= 1
            new_detective = Player(new_tickets, new_pos, detective.name)
            new_detectives = [new_detective if d.name == detective.name else d for d in detectives]
            
            immediate_score = evaluate_position(new_pos, new_detectives, possible_nodes, x_history)
            future_score, _ = alpha_beta_search(
                new_detective, depth - 1, alpha, beta, True,
                possible_nodes, new_detectives, valid_moves, x_history
            )
            
            eval_score = (0.7 * immediate_score) + (0.3 * future_score)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
                
        return min_eval, best_move

# 6. Main Game Logic
def play_move(detective: Player, detectives: List[Player], x_history: List[Tuple[int, str]]) -> Tuple[int, str]:
    """Main function to determine detective's move"""
    global turn, agent
    
    agent = (agent + 1) % 5
    if agent == 0:
        turn += 1
    
    valid_moves = get_valid_moves(detective, detectives)
    if not valid_moves:
        return None
    
    possible_x_locations = set(boardmap.keys())
    
    if turn >= 3 and x_history:
        try:
            last_reveal_index = max(i for i in range(len(reveal_turns)) if reveal_turns[i] <= turn)
            start_index = reveal_turns[last_reveal_index] - 1
            
            if start_index < len(x_history):
                last_known_pos = x_history[start_index][0]
                moves_since_reveal = len(x_history) - start_index - 1
                possible_x_locations = get_possible_locations(x_history, last_known_pos, moves_since_reveal)
                
                if agent == 1:
                    print(f"\nTurn {turn} - Detective {detective.name}'s move")
                    print(f"Last known position: {last_known_pos}")
                    print(f"Moves since last reveal: {moves_since_reveal}")
                    
                    probabilities = print_node_probabilities(possible_x_locations, detectives, x_history)
                    
                    print("\nDetective positions:")
                    for d in detectives:
                        print(f"Detective {d.name}: Node {d.pos}")
                    
                    visualize_traversal_path(last_known_pos, moves_since_reveal,
                                          [t for _, t in x_history[start_index + 1:]])
        except (IndexError, ValueError) as e:
            print(f"Error: {e}")
    
    # Print immediate scores for all moves
    print(f"\nDetective {detective.name} evaluating moves:")
    for move in valid_moves:
        immediate_score = evaluate_position(move[0], detectives, possible_x_locations, x_history)
        print(f"Move to {move[0]} using {move[1]}: immediate score = {immediate_score:.3f}")
    
    # Use alpha-beta search for final decision
    final_score, best_move = alpha_beta_search(
        detective, MAX_DEPTH, -INFINITY, INFINITY, True,
        possible_x_locations, detectives, valid_moves, x_history
    )
    
    if best_move:
        print(f"\nChosen move: {best_move[0]} using {best_move[1]}")
        print(f"Combined score (immediate + future): {final_score:.3f}")
        immediate_score = evaluate_position(best_move[0], detectives, possible_x_locations, x_history)
        print(f"Immediate score: {immediate_score:.3f}")
    
    return best_move if best_move else random.choice(valid_moves)