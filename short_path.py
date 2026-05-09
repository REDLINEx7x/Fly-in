from objects import Zone, Drone, Connection, Graph
from typing import Any, Optional
import heapq


class Solver:
    def __init__(self, graph):

        self.graph = graph

    def find_path(self, start, end, exclude):

        dist_cost = {zone_name: float("inf") for zone_name in self.graph.all_zones}
        dist_cost[start.name] = 0
        previous = {}
        queue = [(0, 0, start)] # (cost, turn, zone_object)
        while queue:
            curr_cost, curr_zone = heapq.heappop(queue)
            print(f"Checking {curr_zone.name}...")
            if curr_zone == end:
                return self._rebuild_path(previous, curr_zone)
            if curr_cost > dist_cost[curr_zone.name]:
                continue
            for neighbor in self.graph.get_neighbors(curr_zone):
                if neighbor.name in exclude:
                    continue

                new_cost = curr_cost + neighbor.movement_cost()

                if new_cost < dist_cost[neighbor.name]:
                    dist_cost[neighbor.name] = new_cost
                    previous[neighbor.name] = curr_zone
                    heapq.heappush(queue, (new_cost, neighbor))

        return []

    def _rebuild_path(self, previous, current_zone):

        path = []
        while current_zone is not None:
            path.append(current_zone)
            current_zone = previous.get(current_zone.name)
        return path[::-1]

    def find_all_paths(self, start, end):

        paths = []
        exclude: set[str] = set()

        while True:

            path = self.find_path(start, end, exclude)
            if  not path:
                break
            paths.append(path)
            exclude.update(z.name for z in path[1:-1])
        return paths

    
