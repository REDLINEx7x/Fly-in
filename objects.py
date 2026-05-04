from typing import Any, Optional
from parser import Parser
from models import ZoneParse, ConnectionParse
from models import ZoneType


class Drone:
    def __iniy__(self, drone_id, current_zone):
        self.drone_id = drone_id
        self.current_zone: Zone = current_zone
        start
        path: list[Zone]
        in_transit: bool = False
        transit_turns_left: int = 0

    def has_arrived(end_zone):
        return self.current_zone == end_zone


class Graph:
    def __init__(self, all_zones, connections, start, end, n_drones):

        self.all_zones = all_zones
        self.connections = connections
        self.start = start
        self.end = end
        self.n_drones = n_drones

    @classmethod
    def from_parsed(cls, parsed: Parser) -> Graph:
        return cls(
            all_zones=parsed.zones.items(),
            connections=parsed.connections,
            start=parsed.start_v.name,
            end=parsed.end_v.name,
            n_drones=parsed.n_drones,
        )

    def get_neighbos(self, zone):

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
        self.neighbors = []

    @classmethod
    def from_parsed(cls, parsed: ZoneParse) -> Zone:

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
                return 2
            return 1


class Connection:

    def __init__(self, zone_a, zone_b, max_capacity):

        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_capacity = max_capacity

    @classmethod
    def from_parsed(cls, parsed: ConnectionParse) -> Connection:

        return cls(
            zone_a=parsed.from_zone,
            zone_b=parsed.to_zone,
        )

    def connected(self, zone):

        if zone == self.zone_a or zone == self.zone_b:
            return True
        return False

    def find_other(self, zone):

        if zone == zone_a:
            return zone_b
        if zone == zone_b:
            return zone_a
        return None
