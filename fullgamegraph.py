import networkx as nx
import matplotlib.pyplot as plt
from board import BOARD

G = nx.Graph()

transport_colors = {
    'taxi': 'yellow',
    'bus': 'blue',
    'underground': 'red',
    'river': 'cyan'
}

for node, connections in BOARD.items():
    for transport, neighbors in connections.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor, color=transport_colors[transport], transport=transport)

edge_colors = [G[u][v]['color'] for u, v in G.edges()]

plt.figure(figsize=(18, 9))
pos = nx.kamada_kawai_layout(G)
nx.draw(G, pos, with_labels=True, node_size=500, font_size=8, edge_color=edge_colors)

legend_elements = [
    plt.Line2D([0], [0], color=color, lw=2, label=transport.capitalize())
    for transport, color in transport_colors.items()
]
plt.legend(handles=legend_elements, loc='upper left', fontsize='large')

plt.title("Scotland Yard Game Board", fontsize=20)
plt.show()
