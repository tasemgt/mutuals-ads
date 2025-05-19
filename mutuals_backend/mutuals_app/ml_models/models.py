# myapp/utils/cluster_model.py

import pickle
import os
from collections import Counter
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, ".")

# Load saved partition (cluster mapping)
with open(os.path.join(MODEL_PATH, "leiden_partition.pkl"), "rb") as f:
    leiden_partition = pickle.load(f)

# Load cluster tags
with open(os.path.join(MODEL_PATH, "cluster_tags.pkl"), "rb") as f:
    cluster_tags = pickle.load(f)

with open(os.path.join(MODEL_PATH, "bipartite_graph.pkl"), "rb") as f:
        bipartite_graph = pickle.load(f)


def assign_new_user_to_cluster(new_user_id, new_user_interests):
    """
    Assign a new user to an existing cluster based on shared interests.
    """
    # Load saved bipartite graph (users + interests) instead of just user graph
    temp_graph = bipartite_graph.copy()

    # Add new user node
    temp_graph.add_node(new_user_id, bipartite=0)

    for interest in new_user_interests:
        # If interest is not already in the graph, skip or optionally add it
        if not temp_graph.has_node(interest):
            continue
        temp_graph.add_edge(new_user_id, interest)

    # Project to user-user graph
    projected = nx.bipartite.weighted_projected_graph(
        temp_graph,
        list(leiden_partition.keys()) + [new_user_id]
    )

    if new_user_id not in projected:
        return {"cluster": None, "tag": "Unassigned"}

    # Extract neighbors with their weights properly
    neighbors = {
        n: projected[new_user_id][n].get('weight', 0)
        for n in projected[new_user_id]
    }

    top_n = 3

    if not neighbors:
        return {"cluster": None, "tag": "Unassigned"}

    # Sort by similarity weight and select top-N
    top_neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:top_n]
    print("Neighs", top_neighbors)

    # Get the clusters of these top-N neighbors
    neighbor_clusters = [
        leiden_partition[n[0]] for n in top_neighbors if n[0] in leiden_partition
    ]

    if neighbor_clusters:
        assigned_cluster = Counter(neighbor_clusters).most_common(1)[0][0]
        tag = cluster_tags.get(assigned_cluster, "Unknown")
    else:
        assigned_cluster = None
        tag = "Unassigned"

    return {"cluster": assigned_cluster, "tag": tag}

# resp = assign_new_user_to_cluster('M0175', ['Cooking','Movies', 'Cars and automobiles'])
# print(resp)