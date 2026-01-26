from pyvis.network import Network
import pandas as pd
import networkx as nx

# Load edges
edges_df = pd.read_csv("edges.csv")

# Create graph
G = nx.Graph()
for _, row in edges_df.iterrows():
    G.add_edge(row['source'], row['target'], edge_type=row['edge_type'])

# Sample small subgraph for clarity
max_nodes = 100
if len(G.nodes) > max_nodes:
    nodes_sample = list(G.nodes)[:max_nodes]
    G = G.subgraph(nodes_sample)

# Assign colors to edge types
unique_edge_types = list(set(nx.get_edge_attributes(G, 'edge_type').values()))
color_palette = [
    "red", "blue", "green", "orange", "purple", "brown", "pink", "cyan", "magenta", "lime"
]
edge_type_color = {etype: color_palette[i % len(color_palette)] for i, etype in enumerate(unique_edge_types)}

# Create PyVis network
net = Network(height="800px", width="100%", notebook=True)
net.from_nx(G)

# Assign edge colors and labels based on edge_type
for edge in net.edges:
    u, v = edge['from'], edge['to']
    etype = G[u][v]['edge_type']
    edge['title'] = etype      # hover tooltip
    edge['label'] = etype      # always visible
    edge['color'] = edge_type_color[etype]

# Add node labels
for node in net.nodes:
    node['title'] = node['id']  # hover shows node id
    node['label'] = node['id']  # display node label

# Show interactive graph
net.show("transaction_graph.html")
