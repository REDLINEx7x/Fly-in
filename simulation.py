from objects import Drone, Zone
from validation import ZoneType


class SimulationManager:

    def __init__(self, graph, solver):

        self.graph = graph
        self.drones: list[Drone] = []
        self.solver = solver

    def setup(self):

        paths = self.solver.find_all_paths(self.graph.start, self.graph.end)
        for i in range(self.graph.n_drones):
            drone = Drone(drone_id=i, current_zone=self.graph.start)
            selected_path = paths[i % len(paths)]
            drone.path = list(selected_path[1:])
            self.drones.append(drone)

    def run_simulation(self):

        self.setup()
        logs = []
        while not all(drone.delivered for drone in self.drones):
            output_transit = self.resolve_transit()
            occupancy = self.zone_occupancy()
            planned, output_moves = self.decide_moves(occupancy)
            self.start_moves(planned)
            full_out = self.output_line(list(output_transit + output_moves))
            self.check_deadlock(full_out)
            logs.append(full_out)
        return logs

    def resolve_transit(self):

        arrive_output = []
        for drone in self.drones:
            if not drone.in_transit:
                continue
            drone.transit_turns_left -= 1
            if drone.transit_turns_left == 0:
                drone.current_zone = drone.transit_target
                drone.in_transit = False
                drone.transit_target = None
                if drone.has_arrived(self.graph.end):
                    drone.delivered = True
                if drone.current_zone == self.graph.end:
                    drone.delivered = True
                arrive_output.append(f"D{drone.drone_id}-{drone.current_zone.name}")
                drone.transit_target = None
            else:
                connection = self.graph.get_connection(
                    drone.current_zone, drone.transit_target
                )
                arrive_output.append(f"D{drone.drone_id}-{connection.name}")
        return arrive_output

    def zone_occupancy(self):

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
        self, occupancy: dict[str, int]
    ) -> tuple[list[tuple[Drone, Zone]], list[str]]:

        planned_moves: list[tuple[Drone, Zone]] = []
        output_str: list[str] = []
        con_usage: dict[frozenset, int] = {}

        for drone in self.drones:
            if drone.in_transit or drone.delivered:
                continue
            if not drone.path:
                continue

            next_zone = drone.path[0]

            if next_zone == self.graph.end:
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
            occupancy[next_zone.name] = occupancy.get(next_zone.name, 0) + 1
            occupancy[drone.current_zone.name] = (
                occupancy.get(drone.current_zone.name, 0) - 1
            )
            con_usage[con_key] = curr_con_usage + 1
        return planned_moves, output_str

    def start_moves(self, planned_moves):

        for drone, next_zone in planned_moves:
            drone.current_zone.current_drones -= 1
            if next_zone.zone_type == ZoneType.RESTRICTED:
                drone.in_transit = True
                drone.transit_turns_left = 1
                drone.transit_target = next_zone
                drone.path.pop(0)
            else:
                drone.current_zone = next_zone
                drone.path.pop(0)
            if drone.current_zone == self.graph.end:
                drone.delivered = True

    def output_line(self, full_output: list[str]):

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
