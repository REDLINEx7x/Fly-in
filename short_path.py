"""Pathfinding module for drone routing."""

from objects import Zone, Graph
from validation import ZoneType
import heapq


class Solver:
    """Finds optimal paths through a zone graph using Dijkstra and DFS."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the solver with a graph.

        Args:
            graph: The zone graph to pathfind on.
        """
        self.graph = graph

    def priority_sort(self, zones: list[Zone]) -> list[Zone]:
        """
        Sort zones to prefer priority zones first.

        """
        priority_zones = [z for z in zones if z.zone_type == "priority"]
        other_zones = [z for z in zones if z.zone_type != "priority"]
        return priority_zones + other_zones

    def find_path(
        self, start: Zone, end: Zone, exclude: set[str] | None = None
    ) -> list[Zone]:
        """Find the shortest path from start to end using Dijkstra.

        Args:
            start: The starting zone.
            end: The destination zone.
            exclude: Zone names to skip during search.

        Returns:
            Ordered list of zones from start to end, or empty if none found.
        """
        if exclude is None:
            exclude = set()

        dist_cost: dict[str, float] = {
            zone_name: float("inf") for zone_name in self.graph.all_zones
        }
        dist_cost[start.name] = 0
        previous: dict[str, Zone] = {}
        queue: list[tuple[float, str]] = [(0, start.name)]

        while queue:
            curr_cost, curr_zone_name = heapq.heappop(queue)
            curr_zone = self.graph.all_zones[curr_zone_name]

            if curr_zone == end:
                return self._rebuild_path(previous, curr_zone)

            if curr_cost > dist_cost[curr_zone_name]:
                continue

            neighbors = [n for n in self.graph.get_neighbors(curr_zone)]
            sort_neibghbors = self.priority_sort(neighbors)

            for neighbor in sort_neibghbors:
                if neighbor.name in exclude:
                    continue
                new_cost = curr_cost + neighbor.movement_cost()
                if new_cost < dist_cost[neighbor.name]:
                    dist_cost[neighbor.name] = new_cost
                    previous[neighbor.name] = curr_zone
                    heapq.heappush(queue, (new_cost, neighbor.name))

        return []

    def _rebuild_path(
        self, previous: dict[str, Zone], current_zone: Zone
    ) -> list[Zone]:
        """Reconstruct path by walking backwards through previous map.

        Args:
            previous: Map of zone name to the zone it was reached from.
            current_zone: The end zone to trace back from.

        Returns:
            Ordered path from start to end.
        """
        path: list[Zone] = []
        zone: Zone | None = current_zone
        while zone is not None:
            path.append(zone)
            zone = previous.get(zone.name)
        return path[::-1]

    def find_all_paths(self, start: Zone, end: Zone) -> list[list[Zone]]:
        """Find all optimal paths from start to end using cost-pruned DFS.

        Args:
            start: The starting zone.
            end: The destination zone.

        Returns:
            All paths whose total cost matches the minimum possible cost.
        """
        first_path = self.find_path(start, end)
        if not first_path:
            return []

        best_cost = sum(zone.movement_cost() for zone in first_path[1:])
        results: list[list[Zone]] = []

        self._recursive_search(start, end, [start], {start.name}, results, 0, best_cost)
        return results

    def _recursive_search(
        self,
        current: Zone,
        end: Zone,
        path: list[Zone],
        visited: set[str],
        results: list[list[Zone]],
        cur_cost: int,
        best_cost: int,
    ) -> None:
        """Recursively explore paths, pruning branches that exceed best cost.

        Args:
            current: Zone currently being explored.
            end: Destination zone.
            path: Path built so far.
            visited: Zone names visited in current path.
            results: Accumulator for complete valid paths.
            cur_cost: Accumulated cost so far.
            best_cost: Maximum allowed cost — prune if exceeded.
        """
        if current == end:
            results.append(list(path))
            return

        for neighbor in self.graph.get_neighbors(current):
            new_cost = cur_cost + neighbor.movement_cost()
            if new_cost > best_cost:
                continue
            if neighbor.name in visited:
                continue
            path.append(neighbor)
            visited.add(neighbor.name)
            self._recursive_search(
                neighbor, end, path, visited, results, new_cost, best_cost
            )
            path.pop()
            visited.discard(neighbor.name)
