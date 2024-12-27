import networkx as nx
import matplotlib.pyplot as plt
from board import BOARD

def visualize_traversal_path(start_node, depth, traversal_path):
    G = nx.Graph()

    # Mapping transport colors as before
    transport_colors = {
        'taxi': 'yellow',
        'bus': 'blue',
        'underground': 'red',
        'river': 'cyan'
    }

    # Build the full graph from BOARD
    for node, connections in BOARD.items():
        for transport, neighbors in connections.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor, color=transport_colors[transport], transport=transport)

    # Function to explore nodes recursively based on the traversal path
    def explore(current_node, remaining_depth, remaining_path, visited):
        if remaining_depth == 0 or not remaining_path:
            return

        transport = remaining_path[0]
        for neighbor in BOARD[current_node].get(transport, []):
            if neighbor not in visited:
                visited.add(neighbor)
                explore(neighbor, remaining_depth - 1, remaining_path[1:], visited)

    # Start traversal
    visited_nodes = {start_node}
    explore(start_node, depth, traversal_path, visited_nodes)

    # Create a subgraph of the visited nodes
    subgraph = G.subgraph(visited_nodes)
    edge_colors = [G[u][v]['color'] for u, v in subgraph.edges()]

    # Plot the graph
    plt.figure(figsize=(12, 6))
    pos = nx.kamada_kawai_layout(subgraph)
    nx.draw(subgraph, pos, with_labels=True, node_size=500, font_size=8, edge_color=edge_colors)

    # Add a legend for transport types
    legend_elements = [
        plt.Line2D([0], [0], color=color, lw=2, label=transport.capitalize())
        for transport, color in transport_colors.items()
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize='large')

    plt.title(f"Traversal Path Visualization from Node {start_node}", fontsize=16)
    plt.show()

    return G