from typing import Any, Optional
from map_parser import Parser
from validation import ZoneParse, ConnectionParse
from validation import ZoneType


class Drone:

    def __init__(self, drone_id, current_zone):
        self.drone_id = drone_id
        self.current_zone: Zone = current_zone
        self.path: list[Zone] = []
        self.in_transit: bool = False
        self.transit_turns_left: int = 0
        self.delivered: bool = False
        self.transit_target: Zone | None

    def has_arrived(self, end_zone):
        return self.current_zone == end_zone


class Graph:

    def __init__(self, all_zones, connections, start, end, n_drones):

        self.all_zones = all_zones
        self.connections = connections
        self.start = start
        self.end = end
        self.n_drones = n_drones

    @classmethod
    def from_parsed(cls, parsed: Parser) -> "Graph":

        logic_zones = {}
        for name, z in parsed.zones.items():
            logic_zones[name] = Zone.from_parsed(z)

        logic_connections = []

        for con in parsed.connections:
            logic_connections.append(Connection.from_parsed(con, logic_zones))
        return cls(
            all_zones=logic_zones,
            connections=logic_connections,
            start=logic_zones[parsed.start_v.name],
            end=logic_zones[parsed.end_v.name],
            n_drones=parsed.drones,
        )

    def get_neighbors(self, zone):

        good_neighbors = []

        for con in self.connections:
            if con.connected(zone):
                finded = con.find_other(zone)
                if not finded.is_blocked():
                    good_neighbors.append(finded)
                else:
                    continue

        return good_neighbors

    def get_connection(self, a, b):

        for con in self.connections:
            if con.connected(a) and con.connected(b):
                return con
        return None


class Zone:

    def __init__(self, name, x, y, zone_type, color, max_drones):

        self.name = name
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.color = color
        self.max_drones = max_drones
        self.current_drones = 0

    @classmethod
    def from_parsed(cls, parsed: ZoneParse) -> "Zone":

        return cls(
            name=parsed.name,
            x=parsed.x,
            y=parsed.y,
            zone_type=parsed.zone_type,
            color=parsed.metadata.get("color", None),
            max_drones=int(parsed.metadata.get("max_drones", 1)),
        )

    def is_blocked(self) -> bool:
        return self.zone_type == ZoneType.BLOCKED

    def movement_cost(self) -> int:
        if self.zone_type == ZoneType.RESTRICTED:
            return 2.0
        if self.zone_type == ZoneType.PRIORITY:
            return 0.9
        if self.zone_type == ZoneType.NORMAL:
            return 1.0


class Connection:

    def __init__(self, zone_a, zone_b, max_link_capacity):

        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    @property
    def name(self) -> str:
        return f"{self.zone_a.name}-{self.zone_b.name}"

    @classmethod
    def from_parsed(
        cls, parsed: ConnectionParse, zone_map: dict[str, Zone]
    ) -> "Connection":

        zone_a = zone_map.get(parsed.from_zone)
        zone_b = zone_map.get(parsed.to_zone)

        if not zone_a or not zone_b:
            raise ValueError(
                f"Connection error: One of the zones ({parsed.from_zone} or {parsed.to_zone}) not found in zone_map"
            )
        return cls(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=int(parsed.metadata.get("max_link_capacity", 1)),
        )

    def connected(self, zone):

        if zone == self.zone_a or zone == self.zone_b:
            return True
        return False

    def find_other(self, zone):

        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        return None
