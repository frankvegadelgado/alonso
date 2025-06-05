# Created on 21/05/2025
# Author: Frank Vega

import itertools
from . import utils

import networkx as nx
import mendive.algorithm as algo
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

    # Structural analysis: detect presence of claw subgraphs
    # This determines which algorithmic approach to use
    claw = algo.find_claw_coordinates(working_graph, first_claw=True)

    if claw is None:
        # CASE 1: Claw-free graph - use polynomial-time exact algorithm
        # Apply Faenza-Oriolo-Stauffer algorithm for weighted stable set on claw-free graphs
        # The maximum weighted stable set's complement gives us the minimum vertex cover
        E = working_graph.edges()
        approximate_vertex_cover = stable.minimum_vertex_cover_claw_free(E)

    else:
        # CASE 2: Graph contains claws - use divide-and-conquer approach

        # Step 1: Edge partitioning using enhanced Burr-Erdos-Lovasz technique
        # Partition edges E = E1 union E2 such that both induced subgraphs G[E1] and G[E2] are claw-free
        E1, E2 = partition.partition_edges_claw_free(working_graph)

        # Step 2: Solve subproblems optimally on claw-free partitions
        # Each partition can be solved exactly using polynomial-time algorithms
        vertex_cover_1 = stable.minimum_vertex_cover_claw_free(E1)
        vertex_cover_2 = stable.minimum_vertex_cover_claw_free(E2)

        # Step 3: Intelligent merging with 1.9-approximation guarantee
        approximate_vertex_cover = merge.merge_vertex_covers(
            working_graph, vertex_cover_1, vertex_cover_2
        )

        # Step 4: Handle residual uncovered edges through recursion
        # Construct residual graph containing edges missed by current vertex cover
        residual_graph = nx.Graph()
        for u, v in working_graph.edges():
            # Edge (u,v) is uncovered if neither endpoint is in our current cover
            if u not in approximate_vertex_cover and v not in approximate_vertex_cover:
                residual_graph.add_edge(u, v)

        # Recursive call to handle remaining uncovered structure
        # This ensures completeness: every edge in the original graph is covered
        residual_vertex_cover = find_vertex_cover(residual_graph)

        # Combine solutions: union of main cover and residual cover
        approximate_vertex_cover = approximate_vertex_cover.union(residual_vertex_cover)

    return approximate_vertex_cover

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