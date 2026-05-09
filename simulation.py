from objects import Drone, Zone, Graph, Connection

class SimulationManager:

    def __init__(self, graph, drones, solver):

        self.graph = graph
        self.drones: list[str] = drones
        self.solver = solver
        self.turn_save = turn_save

    def setup(self):

        paths = self.solver.find_all_paths(self.graph.start, self.graph.end)
        for i in range(self.graph.n_drones):
            drone = Drone(drone_id=i,  current_zone=self.graph.start)
            selected_path = paths[i % len(paths)]
            drone.path = list(selected_path[1:])
            self.drones.append(drone)


    #def run_simulation(self):
    #    while not all(drone.delivered for drone in self.drones):

    def resolve_traffic(self):

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

    def zone_accupancy(self):

        accupancy: dict[str, int] = {}
        for drone in self.drones:
            if drone.delivered:
                continue
            if drone.in_transit:
                continue
            name = drone.current_zone.name
            occupancy[name] = occupancy.get(name, 0) + 1
        return accupancy

    def decide_moves(self, occupancy: dict[str, int]) -> tuple[list[tuple[Drone, Zone]], list[str]]:

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
                capacity_ok = occupancy.get(next_zone.name, 0) < next_zone.max_drones

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
            con_usage[con_key] = curr_con_usage + 1

        return planned_moves, output_str
