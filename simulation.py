from objects import Drone, Zone, Graph
from short_path import Solver
from validation import ZoneType


class SimulationManager:

    def __init__(self, graph: Graph, solver: Solver) -> None:

        self.graph = graph
        self.drones: list[Drone] = []
        self.solver = solver

    def setup(self) -> None:


        paths = self.solver.find_all_paths(self.graph.start, self.graph.end)
        if not paths :
            raise ValueError("No valid path found from start to goal. The map is disconnected.")
        for i in range(self.graph.n_drones):
            drone = Drone(drone_id=i, current_zone=self.graph.start)
            selected_path = paths[i % len(paths)]
            drone.path = list(selected_path[1:])
            self.drones.append(drone)

    def run_simulation(self) -> list[str]:

        self.setup()
        logs = []
        while not all(drone.delivered for drone in self.drones):
            output_transit, just_arrived = self.resolve_transit()
            occupancy = self.zone_occupancy()
            planned, output_moves = self.decide_moves(occupancy, just_arrived)
            self.start_moves(planned)
            full_out = self.output_line(list(output_transit + output_moves))
            self.check_deadlock(full_out)
            if full_out.strip():
                logs.append(full_out)
        return logs

    def resolve_transit(self) -> tuple[list[str], set[int]]:

        arrive_output = []
        just_arrived: set[int] = set()
        for drone in self.drones:
            if not drone.in_transit:
                continue
            drone.transit_turns_left -= 1
            if drone.transit_turns_left == 0:
                if drone.transit_target is None:
                    continue
                drone.current_zone = drone.transit_target
                drone.in_transit = False
                drone.transit_target = None
                if drone.has_arrived(self.graph.end):
                    drone.delivered = True
                # compare by name to avoid relying on Zone.__eq__ semantics
                if drone.current_zone.name == self.graph.end.name:
                    drone.delivered = True
                just_arrived.add(drone.drone_id)
                arrive_output.append(
                    f"D{drone.drone_id}-{drone.current_zone.name}"
                )
            else:
                if drone.transit_target is None:
                    continue
                connection = self.graph.get_connection(
                    drone.current_zone, drone.transit_target
                )
                if connection is None:
                    continue
                arrive_output.append(
                    f"D{drone.drone_id}-{connection.name}"
                )
        return arrive_output, just_arrived

    def zone_occupancy(self) -> dict[str, int]:

        occupancy: dict[str, int] = {}
        for drone in self.drones:
            if drone.delivered:
                continue
            if drone.in_transit:
                continue
            name = drone.current_zone.name
            occupancy[name] = occupancy.get(name, 0) + 1
        return occupancy

    def decide_moves(
        self, occupancy: dict[str, int], just_arrived: set[int]
    ) -> tuple[list[tuple[Drone, Zone]], list[str]]:

        planned_moves: list[tuple[Drone, Zone]] = []
        output_str: list[str] = []
        con_usage: dict[frozenset[str], int] = {}

        for drone in self.drones:
            if drone.in_transit and drone.transit_target is not None:
                con_key = frozenset({drone.current_zone.name, drone.transit_target.name})
                con_usage[con_key] = con_usage.get(con_key, 0) + 1

        for drone in self.drones:
            if drone.in_transit or drone.delivered:
                continue
            if drone.drone_id in just_arrived:
                continue
            if not drone.path:
                continue

            next_zone = drone.path[0]

            # compare by name to avoid relying on object equality
            if next_zone.name == self.graph.end.name:
                capacity_ok = True
            else:
                capacity_ok = (
                    occupancy.get(next_zone.name, 0) < next_zone.max_drones
                )

            if not capacity_ok:
                continue

            con = self.graph.get_connection(drone.current_zone, next_zone)
            if not con:
                continue

            con_key = frozenset({drone.current_zone.name, next_zone.name})
            curr_con_usage = con_usage.get(con_key, 0)

            if curr_con_usage >= con.max_link_capacity:
                continue

            if next_zone.zone_type == ZoneType.RESTRICTED:
                output_str.append(f"D{drone.drone_id}-{con.name}")
            else:
                output_str.append(f"D{drone.drone_id}-{next_zone.name}")

            planned_moves.append((drone, next_zone))
            # increment destination occupancy
            occupancy[next_zone.name] = occupancy.get(next_zone.name, 0) + 1
            # safely decrement origin occupancy and remove when empty
            origin = drone.current_zone.name
            origin_count = occupancy.get(origin, 0) - 1
            if origin_count <= 0:
                occupancy.pop(origin, None)
            else:
                occupancy[origin] = origin_count
            con_usage[con_key] = curr_con_usage + 1
        return planned_moves, output_str

    def start_moves(
        self, planned_moves: list[tuple[Drone, Zone]]
    ) -> None:

        for drone, next_zone in planned_moves:
            if next_zone.zone_type == ZoneType.RESTRICTED:
                drone.in_transit = True
                drone.transit_turns_left = 1
                drone.transit_target = next_zone
                drone.path.pop(0)
            else:
                drone.current_zone = next_zone
                drone.path.pop(0)
            if drone.current_zone.name == self.graph.end.name:
                drone.delivered = True

    def output_line(self, full_output: list[str]) -> str:

        if not full_output:
            return ""

        line = " ".join(full_output)
        return line

    def check_deadlock(self, output_str: str) -> None:
        """Raise an error if the simulation has stalled.

        A deadlock occurs when no drone moved this turn, no drone is
        currently in transit, and not all drones have been delivered.
        """
        if output_str.strip() != "":
            return
        is_anyone_moving = any(drone.in_transit for drone in self.drones)
        is_everyone_delivered = all(drone.delivered for drone in self.drones)

        if not is_anyone_moving and not is_everyone_delivered:
            raise ValueError(
                "ERROR: deadlock happened - No moves possible and no "
                "drones in transit."
            )
