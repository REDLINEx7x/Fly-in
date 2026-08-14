"""Core domain objects for the Fly-in simulation."""

from map_parser import Parser
from validation import ZoneParse, ConnectionParse, ZoneType


class Drone:
    """Represent one drone and its current routing state."""

    def __init__(self, drone_id: int, current_zone: "Zone") -> None:
        self.drone_id = drone_id
        self.current_zone: Zone = current_zone
        self.path: list[Zone] = []
        self.in_transit: bool = False
        self.transit_turns_left: int = 0
        self.delivered: bool = False
        self.transit_target: Zone | None = None

    def has_arrived(self, end_zone: "Zone") -> bool:
        """Check whether the drone is currently at the destination zone."""

        return self.current_zone == end_zone


class Graph:
    """Hold the parsed zone graph, start and end points, and drones."""

    def __init__(
        self,
        all_zones: dict[str, "Zone"],
        connections: list["Connection"],
        start: "Zone",
        end: "Zone",
        n_drones: int,
    ) -> None:

        self.all_zones = all_zones
        self.connections = connections
        self.start = start
        self.end = end
        self.n_drones = n_drones

    @classmethod
    def from_parsed(cls, parsed: Parser) -> "Graph":
        """Build the runtime graph from parsed map data."""

        logic_zones = {}
        for name, z in parsed.zones.items():
            logic_zones[name] = Zone.from_parsed(z)

        logic_connections = [
            Connection.from_parsed(con, logic_zones)
            for con in parsed.connections
        ]
        if parsed.start_v is None or parsed.end_v is None:
            raise ValueError("Start or end zone is missing")
        return cls(
            all_zones=logic_zones,
            connections=logic_connections,
            start=logic_zones[parsed.start_v.name],
            end=logic_zones[parsed.end_v.name],
            n_drones=parsed.drones,
        )

    def get_neighbors(self, zone: "Zone") -> list["Zone"]:
        """Return reachable non-blocked neighboring zones."""

        good_neighbors = []

        for con in self.connections:
            if con.connected(zone):
                finded = con.find_other(zone)
                if finded and not finded.is_blocked():
                    good_neighbors.append(finded)
                else:
                    continue

        return good_neighbors

    def get_connection(
        self, a: "Zone", b: "Zone"
    ) -> "Connection | None":
        """Return the connection shared by two zones, if it exists."""

        for con in self.connections:
            if con.connected(a) and con.connected(b):
                return con
        return None


class Zone:
    """Represent a traversable zone with type, position, and capacity."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType,
        color: str | None,
        max_drones: int,
    ) -> None:

        self.name = name
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.color = color
        self.max_drones = max_drones
        self.current_drones = 0

    @classmethod
    def from_parsed(cls, parsed: ZoneParse) -> "Zone":
        """Convert parsed zone metadata into a runtime zone object."""

        return cls(
            name=parsed.name,
            x=parsed.x,
            y=parsed.y,
            zone_type=parsed.metadata.zone,
            color=parsed.metadata.color,
            max_drones=parsed.metadata.max_drones,
        )

    def is_blocked(self) -> bool:
        """Check whether this zone is inaccessible."""

        return self.zone_type == ZoneType.BLOCKED

    def movement_cost(self) -> int:
        """Return movement cost for this zone based on type."""
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1


class Connection:
    """Represent an undirected link between two zones."""

    def __init__(
        self, zone_a: "Zone", zone_b: "Zone", max_link_capacity: int
    ) -> None:

        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    @property
    def name(self) -> str:
        return f"{self.zone_a.name}-{self.zone_b.name}"

    @classmethod
    def from_parsed(
        cls, parsed: ConnectionParse, zone_map: dict[str, "Zone"]
    ) -> "Connection":
        """Create a runtime connection from parsed endpoints."""

        zone_a = zone_map.get(parsed.from_zone)
        zone_b = zone_map.get(parsed.to_zone)

        if not zone_a or not zone_b:
            raise ValueError(
                f"Connection error: One of the zones ({parsed.from_zone} or "
                f"{parsed.to_zone}) not found in zone_map"
            )
        return cls(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=parsed.metadata.max_link_capacity,
        )

    def connected(self, zone: "Zone") -> bool:
        """Check whether the given zone is one endpoint of this link."""

        if zone == self.zone_a or zone == self.zone_b:
            return True
        return False

    def find_other(self, zone: "Zone") -> "Zone | None":
        """Return the opposite endpoint for a connected zone."""

        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        return None
