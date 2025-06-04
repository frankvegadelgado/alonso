# Created on 21/05/2025
# Author: Frank Vega

import itertools
from . import utils

import networkx as nx
from . import partition
from . import stable
from . import merge

def find_vertex_cover(graph):
    """
    Compute an approximate minimum vertex cover set for an undirected graph by transforming it into a chordal graph.

    Args:
        graph (nx.Graph): A NetworkX Graph object representing the input graph.

    Returns:
        set: A set of vertex indices representing the approximate minimum vertex cover set.
             Returns an empty set if the graph is empty or has no edges.
    """
    # Validate that the input is a valid undirected NetworkX graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
    
    # Handle trivial cases: return empty set for graphs with no nodes or no edges
    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return set()  # No vertices or edges mean no cover is needed
    
    # Create a working copy to avoid modifying the original graph
    working_graph = graph.copy()
    
    # Remove self-loops as they are irrelevant for vertex cover computation
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
    
    # Remove isolated nodes (degree 0) since they don't contribute to the vertex cover
    working_graph.remove_nodes_from(list(nx.isolates(working_graph)))
    
    # Return empty set if the cleaned graph has no nodes after removals
    if working_graph.number_of_nodes() == 0:
        return set()
    
    # Partition edges into two subsets (E1, E2) using the Burr-Erdős-Lovász (1976) algorithm
    # This step divides the graph into two claw-free subgraphs
    # Complexity: O(m * (m * Δ * C + C^2)), where m is edges, Δ is maximum degree, C is number of claws
    E1, E2 = partition.partition_edges_claw_free(working_graph)
    
    # Compute minimum vertex cover for E1 using the Faenza, Oriolo & Stauffer (2011) algorithm
    # This finds the maximum weighted stable set in the claw-free graph E1, whose complement is the vertex cover
    # Complexity: O(n^3), where n is the number of nodes in the subgraph induced by E1
    vertex_cover_1 = stable.minimum_vertex_cover_claw_free(E1)
    
    # Compute minimum vertex cover for E2 using the same Faenza, Oriolo & Stauffer (2011) algorithm
    # Complexity: O(n^3) for the subgraph induced by E2
    vertex_cover_2 = stable.minimum_vertex_cover_claw_free(E2)

    # Merge the two vertex covers from E1 and E2 to approximate the minimum vertex cover of the original graph
    approximate_vertex_cover = merge.merge_vertex_covers(E1, E2, vertex_cover_1, vertex_cover_2)
    
    # Create a residual graph containing edges not covered by the current vertex cover
    residual_graph = nx.Graph()
    for u, v in working_graph.edges():
        if u not in approximate_vertex_cover and v not in approximate_vertex_cover:
            residual_graph.add_edge(u, v)  # Add edge if neither endpoint is in the cover
    
    # Recursively find vertex cover for the residual graph to handle uncovered edges
    residual_vertex_cover = find_vertex_cover(residual_graph)
    
    # Combine the approximate vertex cover with the residual cover to ensure all edges are covered
    return approximate_vertex_cover.union(residual_vertex_cover)

def find_vertex_cover_brute_force(graph):
    """
    Computes an exact minimum vertex cover in exponential time.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the exact vertex cover, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    n_vertices = len(graph.nodes())

    for k in range(1, n_vertices + 1): # Iterate through all possible sizes of the cover
        for candidate in itertools.combinations(graph.nodes(), k):
            cover_candidate = set(candidate)
            if utils.is_vertex_cover(graph, cover_candidate):
                return cover_candidate
                
    return None



def find_vertex_cover_approximation(graph):
    """
    Computes an approximate vertex cover in polynomial time with an approximation ratio of at most 2 for undirected graphs.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the approximate vertex cover, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    #networkx doesn't have a guaranteed minimum vertex cover function, so we use approximation
    vertex_cover = nx.approximation.vertex_cover.min_weighted_vertex_cover(graph)
    return vertex_cover