import networkx as nx
import matplotlib.pyplot as plts
import random
import time
import matplotlib.animation as animation
from collections import defaultdict

def walk_on_graph_animation(G, max_points, output_file):
    # Find nodes with no inbound edges
    nodes_no_inbound_edges = [node for node in G.nodes() if G.in_degree(node) == 0]
    # Find nodes with no outbound edges
    nodes_no_outbound_edges = [node for node in G.nodes() if G.out_degree(node) == 0]
    # Get all nodes in the graph
    all_nodes = list(G.nodes())

    fig, ax = plts.subplots()
    pos = nx.spiral_layout(G)  # You can use other layout algorithms if preferred

    points = []  # Initialize empty list to hold points

    def update(num):
        ax.clear()
        # Initialize counts of points in each vertex for this round
        points_in_vertices = defaultdict(int)

        # Randomly choose the number of points to add at the start vertices
        num_points = random.randint(0, max_points)
        # Add new points at random starting nodes with no inbound edge
        new_points = [{'current_node': random.choice(nodes_no_inbound_edges)} for _ in range(num_points)]
        points.extend(new_points)  # Add new points to the existing points list

        # Iterate through each point
        for point in points:
            current_node = point['current_node']
            # Increment count of points in current node
            points_in_vertices[current_node] += 1

            # If the current node has no outbound edges, remove the point
            if current_node in nodes_no_outbound_edges:
                points.remove(point)
                continue

            # Get all outbound edges and their normalized weights
            outbound_edges = list(G.out_edges(current_node, data='weight'))
            # Extract normalized weights
            weights = [weight for _, _, weight in outbound_edges]
            # Choose the next node based on normalized weights
            next_node_index = random.choices(range(len(outbound_edges)), weights=weights)[0]
            next_node = outbound_edges[next_node_index][1]

            # Move the point to the next node
            point['current_node'] = next_node

        # Draw the graph with nodes colored based on the number of visiting points
        node_colors = [points_in_vertices[node] for node in all_nodes]
        nx.draw(G, pos, ax=ax, with_labels=True, node_size=700, node_color=node_colors, cmap='Oranges', font_size=12, font_weight='normal', arrowsize=10)
        
        # Display the points in each vertex for this round
        for node, count in points_in_vertices.items():
            ax.text(pos[node][0], pos[node][1], f"{count}", bbox=dict(facecolor='white', alpha=0.5))

        ax.set_title(f"Round {num}: Points in vertices")

        # Write counts to the output file
        with open(output_file, 'a') as f:
            f.write(f"Round {num}: {dict(points_in_vertices)}\n")

    ani = animation.FuncAnimation(fig, update, frames=range(50), interval=5000, repeat=False)
    plts.axis('off')
    plts.show()


def read_graph_from_file(file_path):
    G = nx.DiGraph()
    with open(file_path, 'r') as file:
        num_nodes, num_edges = map(int, file.readline().split())
        for _ in range(num_edges):
            source, destination, weight = map(int, file.readline().split())
            G.add_edge(str(source), str(destination), weight=weight)
    return G

# Read the graph from file
file_path = 'graph_details.txt'  # Change this to your file path
G = read_graph_from_file(file_path)

# Calculate the sum of outbound edge weights for each vertex
outbound_edge_sums = {node: sum(weight for _, _, weight in G.out_edges(node, data='weight')) for node in G.nodes()}

# Normalize the edge weights and update the edge labels
normalized_edge_labels = {}
for edge in G.edges(data=True):
    source, destination, weight = edge
    normalized_weight = weight['weight'] / outbound_edge_sums[source] if outbound_edge_sums[source] != 0 else 0
    normalized_edge_labels[(source, destination)] = f"{weight['weight']} ({normalized_weight:.2f})"

# Draw the graph
# pos = nx.spiral_layout(G)
# nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=12, font_weight='normal', arrowsize=10)

# # Add edge labels with original and normalized weight values
# nx.draw_networkx_edge_labels(G, pos, edge_labels=normalized_edge_labels)

# Find nodes with no inbound edges
nodes_no_inbound_edges = [node for node in G.nodes() if G.in_degree(node) == 0]

# Find nodes with no outbound edges
nodes_no_outbound_edges = [node for node in G.nodes() if G.out_degree(node) == 0]

print("Nodes with no inbound edges:", nodes_no_inbound_edges)
print("Nodes with no outbound edges:", nodes_no_outbound_edges)

# Simulate multiple points walking on the graph
walk_on_graph_animation(G, max_points=3, output_file='output.txt')

# Display the graph
# plts.title('Weighted Directed Graph with Normalized Edge Weights')
# plts.axis('off')
# plts.show()