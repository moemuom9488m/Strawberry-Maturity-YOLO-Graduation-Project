import numpy as np
import heapq

class AStarPlanner:
    def __init__(self, grid_map, resolution=0.1):
        """
        A* Path Planner
        :param grid_map: 2D numpy array (0 for obstacles, 1 for free space)
        :param resolution: Physical distance per grid cell (meters)
        """
        self.grid = grid_map
        self.rows, self.cols = grid_map.shape
        self.resolution = resolution
        
    def heuristic(self, a, b):
        """Euclidean distance heuristic"""
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def get_neighbors(self, node):
        """Get 8-connected neighbors (up, down, left, right, diagonals)"""
        neighbors = []
        # Directions: 8-connectivity
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < self.rows and 0 <= y < self.cols:
                if self.grid[x, y] == 1: # Free space
                    # Cost is 1.414 for diagonals, 1.0 for straight
                    cost = np.sqrt(dx**2 + dy**2)
                    neighbors.append(((x, y), cost))
        return neighbors

    def plan(self, start_m, goal_m):
        """
        Plan path from start to goal in physical meters
        :param start_m: (y_meters, x_meters)
        :param goal_m: (y_meters, x_meters)
        :return: List of coordinates in meters
        """
        # Convert meters to grid indices
        start = (int(start_m[0] / self.resolution), int(start_m[1] / self.resolution))
        goal = (int(goal_m[0] / self.resolution), int(goal_m[1] / self.resolution))

        # Check validity
        if not (0 <= start[0] < self.rows and 0 <= start[1] < self.cols):
            print(f"Error: Start {start} out of bounds")
            return None
        if not (0 <= goal[0] < self.rows and 0 <= goal[1] < self.cols):
            print(f"Error: Goal {goal} out of bounds")
            return None
        if self.grid[start] == 0:
            print(f"Warning: Start {start} is in obstacle")
        if self.grid[goal] == 0:
            print(f"Warning: Goal {goal} is in obstacle")

        # Priority queue: (f_score, current_node)
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor, cost in self.get_neighbors(current):
                tentative_g_score = g_score[current] + cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None # No path found

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        # Convert back to meters
        return [(p[0] * self.resolution, p[1] * self.resolution) for p in path]

def generate_skip_row_targets(field_w, field_l, row_spacing=0.8, trench_w=0.7, resolution=0.1):
    """
    Generate target waypoints for Skip-Row coverage
    """
    rows = []
    # Simplified logic: every other row or specific pattern
    # period = row_spacing + trench_w
    # ... logic to define waypoints along rows ...
    pass
