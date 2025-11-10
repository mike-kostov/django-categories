from collections import defaultdict, deque
from .models import Category, CategorySimilarity

class CategoryGraphService:
    def __init__(self):
        # In memory graph representation: {category_id: [similar_id1, similar_id2, ...]}
        self.adjacency_list = defaultdict(list)
        self.all_category_ids = set(Category.objects.values_list('id', flat=True))

        # Build the graph
        self._build_graph()

    def _build_graph(self):
        """Builds the undirected graph from the CategorySimilarity table."""

        # Load all similarity pairs efficiently in one query
        similarities = CategorySimilarity.objects.all().values_list(
            'category_a_id', 'category_b_id'
        )

        for id_a, id_b in similarities:
            # Since similarity is bidirectional, add the edge in both directions
            self.adjacency_list[id_a].append(id_b)
            self.adjacency_list[id_b].append(id_a)

        # Ensure all categories are in the adjacency list, even if isolated
        for cat_id in self.all_category_ids:
            if cat_id not in self.adjacency_list:
                self.adjacency_list[cat_id] = []

    def find_shortest_path(self, start_id, end_id):
        """Finds the shortest sequence (rabbit hole) from start to end."""
        if start_id == end_id:
            return [start_id]

        queue = deque([start_id])
        visited = {start_id}
        # Parent map to reconstruct the path: {child_id: parent_id}
        parent_map = {start_id: None}

        while queue:
            current_id = queue.popleft()

            for neighbor_id in self.adjacency_list.get(current_id, []):
                if neighbor_id == end_id:
                    # Found the end, reconstruct path
                    path = [end_id]
                    while current_id is not None:
                        path.append(current_id)
                        current_id = parent_map.get(current_id)
                    return path[::-1] # Reverse the path to go start -> end

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent_map[neighbor_id] = current_id
                    queue.append(neighbor_id)

        return None # Path not found

    def get_rabbit_islands(self):
        """Finds all connected components (rabbit islands)."""
        visited = set()
        islands = []

        for start_node in self.all_category_ids:
            if start_node not in visited:
                island = []
                stack = [start_node] # Using a stack for DFS

                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        island.append(node)

                        # Add unvisited neighbors to the stack
                        for neighbor in self.adjacency_list.get(node, []):
                            if neighbor not in visited:
                                stack.append(neighbor)

                if island:
                    islands.append(island)

        return islands

    def find_longest_rabbit_hole(self):
        """
        Finds the longest shortest path (graph diameter) in the largest island.
        This is O(N * (N+E)), which is slow, so we use the two-BFS approximation
        on the largest component for robustness.
        """
        islands = self.get_rabbit_islands()
        if not islands:
            return []

        # Find the largest island
        largest_island = max(islands, key=len, default=[])

        if not largest_island:
            return []

        # 1. Run BFS from a random node (A) in the largest island to find the farthest node (B)
        start_node = largest_island[0]
        farthest_node_b, _, parent_map_a = self._bfs_farthest(start_node)

        # 2. Run BFS from B to find the farthest node (C)
        farthest_node_c, max_distance, parent_map_b = self._bfs_farthest(farthest_node_b)

        # 3. Reconstruct the path B -> C
        path = [farthest_node_c]
        current = parent_map_b.get(farthest_node_c)
        while current is not None:
            path.append(current)
            current = parent_map_b.get(current)

        return path[::-1] # Longest path B -> C

    def _bfs_farthest(self, start_id):
        """Helper to run BFS and return the farthest node and path map."""
        queue = deque([(start_id, 0)]) # (node, distance)
        visited = {start_id}
        parent_map = {start_id: None}
        max_dist = 0
        farthest_node = start_id

        while queue:
            current_id, dist = queue.popleft()

            if dist > max_dist:
                max_dist = dist
                farthest_node = current_id

            for neighbor_id in self.adjacency_list.get(current_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent_map[neighbor_id] = current_id
                    queue.append((neighbor_id, dist + 1))

        return farthest_node, max_dist, parent_map
