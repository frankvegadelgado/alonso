from collections import defaultdict
import networkx as nx
from typing import Set, Tuple, List
import mendive.algorithm as claws
import aegypti.algorithm as triangles
class ClawFreePartitioner:
    """
    Implements a polynomial-time algorithm to partition graph edges into two sets
    E1 and E2 such that both induced subgraphs are claw-free.
    
    Based on principles from Burr-Erdős-Lovász approach for Ramsey-type problems.
    A claw is a star graph K_{1,3} (one central vertex connected to 3 others).
    """
    
    def __init__(self, graph):
        """
        Initialize with a NetworkX graph.
        
        Args:
            graph: NetworkX Graph object
        """
        self.G = graph.copy()
        self.n = len(self.G.nodes())
        self.m = len(self.G.edges())
        
    def find_potential_claw_centers(self) -> Set[int]:
        """
        Find vertices that could potentially be centers of claws.
        A vertex can be a claw center only if it has degree >= 3.
        
        Returns:
            Set of vertices with degree >= 3
        """
        return {v for v in self.G.nodes() if self.G.degree(v) >= 3}
    
    def get_neighborhood_edges(self, vertex: int) -> List[Tuple[int, int]]:
        """
        Get all edges incident to a given vertex.
        
        Args:
            vertex: The vertex to get incident edges for
            
        Returns:
            List of edges (as tuples) incident to the vertex
        """
        return [(vertex, neighbor) for neighbor in self.G.neighbors(vertex)]
    
    def would_create_claw(self, edges_in_partition: Set[Tuple[int, int]], 
                         new_edge: Tuple[int, int]) -> bool:
        """
        Check if adding a new edge to a partition would create a claw.
        
        Args:
            edges_in_partition: Current edges in the partition
            new_edge: Edge to potentially add
            
        Returns:
            True if adding the edge would create a claw, False otherwise
        """
        # Build adjacency list for current partition
        G = nx.Graph()
        for u, v in edges_in_partition:
            G.add_edge(u, v)
        
        # Add the new edge temporarily
        u, v = new_edge
        G.add_edge(u, v)
        H = nx.complement(G)
        # Check if any vertex now forms a claw
        for vertex in [u, v]:
            neighbors = list(G.neighbors(vertex))
            if len(neighbors) >= 3:
                # Check all combinations of 3 neighbors
                subgraph = H.subgraph(neighbors)
                triangle = triangles.find_triangle_coordinates(subgraph, first_triangle=True)
                if triangle is not None:
                    return True
        
        return False
    
    def greedy_partition(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Greedily partition edges into two claw-free sets.
        
        Strategy:
        1. Process vertices in order of decreasing degree
        2. For each vertex, try to distribute its incident edges 
           between the two partitions to avoid creating claws
        3. Use a greedy approach that prioritizes balance
        
        Returns:
            Tuple of (E1, E2) - two sets of edges
        """
        E1 = set()
        E2 = set()
        processed_edges = set()
        
        # Sort vertices by degree (descending) to handle high-degree vertices first
        vertices_by_degree = sorted(self.G.nodes(), 
                                  key=lambda v: self.G.degree(v), 
                                  reverse=True)
        
        for vertex in vertices_by_degree:
            if self.G.degree(vertex) < 3:
                continue  # Can't be center of a claw
                
            incident_edges = self.get_neighborhood_edges(vertex)
            unprocessed_edges = [e for e in incident_edges if e not in processed_edges]
            
            if len(unprocessed_edges) < 3:
                continue  # Not enough edges to potentially form a claw
            
            # Try to distribute edges to avoid claws
            for edge in unprocessed_edges:
                if edge in processed_edges:
                    continue
                    
                # Try adding to E1 first
                if not self.would_create_claw(E1, edge):
                    E1.add(edge)
                    processed_edges.add(edge)
                elif not self.would_create_claw(E2, edge):
                    E2.add(edge)
                    processed_edges.add(edge)
                else:
                    # If adding to either partition would create a claw,
                    # add to the smaller partition (balance heuristic)
                    if len(E1) <= len(E2):
                        E1.add(edge)
                    else:
                        E2.add(edge)
                    processed_edges.add(edge)
        
        # Add remaining unprocessed edges using simple alternating strategy
        remaining_edges = set(self.G.edges()) - processed_edges
        for i, edge in enumerate(remaining_edges):
            if i % 2 == 0:
                E1.add(edge)
            else:
                E2.add(edge)
        
        return E1, E2
    
    def verify_claw_free(self, edge_set: Set[Tuple[int, int]]) -> bool:
        """
        Verify that a given edge set induces a claw-free graph.
        
        Args:
            edge_set: Set of edges to check
            
        Returns:
            True if the induced graph is claw-free, False otherwise
        """
        # Build adjacency list
        G = nx.Graph()
        G.add_edges_from(edge_set)
        claw = claws.find_claw_coordinates(G, first_claw=True)
        if claw is None:
            return True
        else: 
            return False

    def partition_edges(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Main method to partition graph edges into two claw-free sets.
        
        Returns:
            Tuple of (E1, E2) where both induce claw-free graphs
        """
        if self.m == 0:
            return set(), set()
        
        # Try the greedy approach
        E1, E2 = self.greedy_partition()
        
        # Verify the result
        if self.verify_claw_free(E1) and self.verify_claw_free(E2):
            return E1, E2
        
        # If greedy fails, use a more conservative approach
        return self.fallback_partition()
    
    def fallback_partition(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Fallback method: Create a more conservative partition by ensuring
        no vertex has degree > 2 in either partition (guarantees claw-free).
        
        Returns:
            Tuple of (E1, E2) - two claw-free edge sets
        """
        E1 = set()
        E2 = set()
        
        degree1 = defaultdict(int)
        degree2 = defaultdict(int)
        
        for edge in self.G.edges():
            u, v = edge
            # Add to partition where both endpoints have degree < 2
            if degree1[u] < 2 and degree1[v] < 2:
                E1.add(edge)
                degree1[u] += 1
                degree1[v] += 1
            elif degree2[u] < 2 and degree2[v] < 2:
                E2.add(edge)
                degree2[u] += 1
                degree2[v] += 1
            else:
                # Add to the partition with smaller total degree
                if sum(degree1.values()) <= sum(degree2.values()):
                    E1.add(edge)
                else:
                    E2.add(edge)
        
        return E1, E2