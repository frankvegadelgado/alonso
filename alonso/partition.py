import networkx as nx
from typing import Tuple, Set, List
from collections import defaultdict
import itertools
import mendive.algorithm as algo

class BurrErdosLovaszPartitioner:
    """
    Implementation of the Burr-Erdős-Lovász (1976) algorithm for partitioning
    edges of a graph into two subsets such that each subset induces a k-star-free subgraph.
    
    For k=3 (claw-free case), we partition edges to avoid 3-stars in each partition.
    
    The algorithm works by maintaining two edge sets and for each new edge,
    assigning it to the partition where it creates the fewest violations,
    then locally repairing any violations that arise.
    """
    
    def __init__(self, graph: nx.Graph, k: int = 3):
        self.graph = graph.copy()
        self.k = k  # k=3 for claw-free (3-star-free)
        self.n = len(graph.nodes())
        
    def partition_edges(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Partition edges into two k-star-free subgraphs using BEL algorithm.
        """
        E1 = set()
        E2 = set()
        
        # Convert edges to consistent format
        edges = [(min(u, v), max(u, v)) for u, v in self.graph.edges()]
        
        # Main algorithm: assign each edge to minimize violations
        for edge in edges:
            # Count violations if we add edge to E1
            violations_E1 = self._count_violations_after_adding(E1, edge)
            violations_E2 = self._count_violations_after_adding(E2, edge)
            
            # Add to partition with fewer violations
            if violations_E1 <= violations_E2:
                E1.add(edge)
                # Repair violations in E1
                E1 = self._repair_violations(E1)
            else:
                E2.add(edge)
                # Repair violations in E2
                E2 = self._repair_violations(E2)
        
        return E1, E2
    
    def _count_violations_after_adding(self, edge_set: Set[Tuple[int, int]], 
                                     new_edge: Tuple[int, int]) -> int:
        """Count number of k-stars that would be created by adding new_edge."""
        temp_set = edge_set | {new_edge}
        return self._count_k_stars(temp_set)
    
    def _is_claw_free(self, edge_set: Set[Tuple[int, int]]) -> bool:
        """Count number of k-stars in the edge set."""
        if not edge_set:
            return True
            
        # Build graph from edge set
        G = nx.Graph()
        G.add_edges_from(edge_set)
        
        claw = algo.find_claw_coordinates(G, first_claw=True)
        if claw is None:
            return True
        else:
            return False
    
    
    def _count_k_stars(self, edge_set: Set[Tuple[int, int]]) -> int:
        """Count number of k-stars in the edge set."""
        if not edge_set:
            return 0
            
        # Build graph from edge set
        G = nx.Graph()
        G.add_edges_from(edge_set)
        
        k_star_count = 0
        
        if self.k == 3:
          all_claws = algo.find_claw_coordinates(G, first_claw=False)
          if all_claws is not None:
            k_star_count = len(all_claws)
        else:
            # Check each vertex as potential center of k-star
            for center in G.nodes():
                neighbors = list(G.neighbors(center))
                if len(neighbors) >= self.k:
                    # Count k-subsets of neighbors that form independent sets
                    for k_subset in itertools.combinations(neighbors, self.k):
                        # Check if this k-subset is independent
                        is_independent = True
                        for i in range(self.k):
                            for j in range(i + 1, self.k):
                                if G.has_edge(k_subset[i], k_subset[j]):
                                    is_independent = False
                                    break
                            if not is_independent:
                                break
                        
                        if is_independent:
                            k_star_count += 1
            
        return k_star_count
    
    def _repair_violations(self, edge_set: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """
        Repair k-star violations in edge_set by removing minimal edges.
        This is the key part of the BEL algorithm.
        """
        if not edge_set:
            return edge_set
            
        current_set = edge_set.copy()
        
        while True:
            if self.k == 3:
                is_claw_free = self._is_claw_free(current_set)
                if is_claw_free:
                    break  # No more violations
                violations = self._find_k_stars(current_set)
            else:        
                violations = self._find_k_stars(current_set)
                if not violations:
                    break  # No more violations
                
            # Find the edge that appears in most violations
            edge_violation_count = defaultdict(int)
            for k_star in violations:
                center, leaves = k_star
                # Each k-star consists of k edges from center to leaves
                for leaf in leaves:
                    edge = (min(center, leaf), max(center, leaf))
                    if edge in current_set:
                        edge_violation_count[edge] += 1
            
            if not edge_violation_count:
                break
                
            # Remove the edge that appears in most violations
            most_violating_edge = max(edge_violation_count.keys(), 
                                    key=lambda e: edge_violation_count[e])
            current_set.remove(most_violating_edge)
        
        return current_set
    
    def _find_k_stars(self, edge_set: Set[Tuple[int, int]]) -> List[Tuple[int, Tuple]]:
        """Find all k-stars in the edge set. Returns list of (center, leaves) tuples."""
        if not edge_set:
            return []
            
        # Build graph from edge set
        G = nx.Graph()
        G.add_edges_from(edge_set)
        
        k_stars = []
        
        if self.k == 3:
          all_claws = algo.find_claw_coordinates(G, first_claw=False)
          if all_claws is not None:
            for subset in all_claws:
                subgraph = G.subgraph(subset)
                sorted_nodes = sorted(list(subset), key=lambda x: subgraph.degree(x))
                center = sorted_nodes.pop()
                k_subset = tuple(sorted_nodes)
                k_stars.append((center, k_subset))
        else:
          # Check each vertex as potential center of k-star
          for center in G.nodes():
              neighbors = list(G.neighbors(center))
              if len(neighbors) >= self.k:
                  # Find all k-subsets of neighbors that form independent sets
                  for k_subset in itertools.combinations(neighbors, self.k):
                      # Check if this k-subset is independent
                      is_independent = True
                      for i in range(self.k):
                          for j in range(i + 1, self.k):
                              if G.has_edge(k_subset[i], k_subset[j]):
                                  is_independent = False
                                  break
                          if not is_independent:
                              break
                      
                      if is_independent:
                          k_stars.append((center, k_subset))
          
        return k_stars
    
    def verify_partition(self, E1: Set[Tuple[int, int]], E2: Set[Tuple[int, int]]) -> Tuple[bool, bool]:
        """Verify that both partitions are k-star-free."""
        if self.k == 3:
            return (self._is_claw_free(E1), self._is_claw_free(E2))
        else:    
            return (self._count_k_stars(E1) == 0, self._count_k_stars(E2) == 0)


def partition_edges_claw_free(G: nx.Graph) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
    """
    Partition edges of graph G into two sets such that each induces a claw-free subgraph.
    
    Implementation of Burr, Erdős, Lovász (1976) algorithm for k=3 (claw-free case).
    
    Args:
        G: Undirected NetworkX graph
        
    Returns:
        (E1, E2): Two edge sets that induce claw-free subgraphs
    """
    partitioner = BurrErdosLovaszPartitioner(G, k=3)
    return partitioner.partition_edges()

