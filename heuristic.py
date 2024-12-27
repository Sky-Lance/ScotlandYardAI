import networkx as nx
from engine.player import Player
from engine import boardmap
from typing import List, Tuple, Set, Dict
import random
from path import visualize_traversal_path
from functools import lru_cache

# Global variables aligned with game state
turn = 1
agent = 0
reveal_turns = [3, 8, 13, 18, 24]

@lru_cache(maxsize=1024)
def get_valid_transport_moves(pos: int, transport_type: str) -> Set[int]:
    """Cache transport connections for performance"""
    return set(boardmap[pos].get(transport_type, []))

def get_possible_locations(x_history: List[Tuple[int, str]], last_known_pos: int, moves_since_reveal: int) -> Set[int]:
    """Calculate possible Mr. X locations from last reveal"""
    possible_nodes = {last_known_pos}
    
    for _, transport in x_history[-moves_since_reveal:]:
        next_possible = set()
        for node in possible_nodes:
            if node in boardmap:
                next_possible.update(get_valid_transport_moves(node, transport))
        possible_nodes = next_possible
    
    return possible_nodes

def evaluate_move(pos: int, detectives: List[Player], possible_x_locations: Set[int]) -> float:
    """Evaluate move based on coverage and distance to possible X locations"""
    if not possible_x_locations:
        return 0.0
    
    score = 0.0
    detective_positions = {d.pos for d in detectives}
    
    for x_pos in possible_x_locations:
        # Calculate minimum distance from any detective
        min_detective_distance = min(len(nx.shortest_path(nx.Graph(boardmap), d.pos, x_pos)) - 1 
                                   for d in detectives)
        
        # Calculate distance from current position
        current_distance = len(nx.shortest_path(nx.Graph(boardmap), pos, x_pos)) - 1
        
        # Score based on distance and coverage
        position_score = 10.0 / (1.0 + current_distance)
        
        # Bonus if this detective would be closest
        if current_distance <= min_detective_distance:
            position_score *= 1.5
            
        # Penalty for overlapping with other detectives
        if pos in detective_positions:
            position_score *= 0.5
            
        score += position_score
    
    return score / len(possible_x_locations)

def get_valid_moves(detective: Player, detectives: List[Player]) -> List[Tuple[int, str]]:
    """Get all valid moves for the detective"""
    valid_moves = []
    detective_positions = {d.pos for d in detectives}
    
    for transport, count in detective.tickets.items():
        if count <= 0:
            continue
            
        for next_pos in get_valid_transport_moves(detective.pos, transport):
            if next_pos not in detective_positions:
                valid_moves.append((next_pos, transport))
    
    return valid_moves

def play_move(detective: Player, detectives: List[Player], x_history: List[Tuple[int, str]]) -> Tuple[int, str]:
    """Main function to determine detective's move"""
    global turn, agent
    
    # Update turn counters
    agent = (agent + 1) % 5
    if agent == 0:
        turn += 1
    
    # Get valid moves
    valid_moves = get_valid_moves(detective, detectives)
    if not valid_moves:
        return None
    
    # Calculate possible X locations
    possible_x_locations = set(boardmap.keys())  # Default to all locations
    
    if turn >= 3 and x_history:
        try:
            # Find last reveal
            last_reveal_index = max(i for i in range(len(reveal_turns)) if reveal_turns[i] <= turn)
            start_index = reveal_turns[last_reveal_index] - 1
            
            if start_index < len(x_history):
                last_known_pos = x_history[start_index][0]
                moves_since_reveal = len(x_history) - start_index - 1
                
                possible_x_locations = get_possible_locations(x_history, last_known_pos, moves_since_reveal)
                
                if agent == 1:
                    print(f"Possible X locations (Turn {turn}): {possible_x_locations}")
                    visualize_traversal_path(last_known_pos, moves_since_reveal,
                                          [t for _, t in x_history[start_index + 1:]])
        except (IndexError, ValueError):
            pass
    
    # Evaluate and choose best move
    best_score = float('-inf')
    best_move = None
    
    for move in valid_moves:
        score = evaluate_move(move[0], detectives, possible_x_locations)
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move if best_move else random.choice(valid_moves)