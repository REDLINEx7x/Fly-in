"""Parser for drone simulation map configuration files.

Handles parsing and validation of map files containing zones, connections,
and drone count specifications according to subject requirements.
"""

from validation import (
    DroneParse, ZoneParse, ConnectionParse, ZoneType,
    ZoneMetadata, ConnectionMetadata,
)
from pydantic import ValidationError
from typing import Optional
import re


class Parser:
    """Parses and validates drone simulation map configuration files."""

    def __init__(self, file_path: str) -> None:
        """Initialize parser with file path.

        Args:
            file_path: Path to the map configuration file.
        """
        self.path_config = file_path
        self.drones: int = 0
        self.zones: dict[str, ZoneParse] = {}
        self.connections: list[ConnectionParse] = []
        self.seen_connections: set[frozenset[str]] = set()
        self.start_v: Optional[ZoneParse] = None
        self.end_v: Optional[ZoneParse] = None
        self.drones_line = False

    def extract_metadata(self, line: str, line_num: int) -> tuple[str, dict[str, str]]:
        """Extract metadata from bracketed section of a line.

        Args:
            line: The line to extract metadata from.
            line_num: The line number (for error reporting).

        Returns:
            Tuple of (clean_line, metadata_dict).

        Raises:
            ValueError: If metadata format is invalid.
        """
        match = re.search(r"\[(.*?)\]", line)
        clean_line = line
        metadata_dict = {}

        if match:
            meta_data = match.group(1)
            clean_line = line.replace(match.group(0), "").strip()

            for item in meta_data.split():
                if "=" not in item:
                    raise ValueError(
                        f"Line {line_num}: Metadata format invalid for '{item}'. "
                        "Expected 'key=value'."
                    )

                key, value = item.split("=", 1)
                metadata_dict[key] = value

        return clean_line, metadata_dict

    def parse_drones(self, line: str, line_num: int) -> None:
        """Parse drone count from first line.

        Args:
            line: The line to parse.
            line_num: The line number (for error reporting).

        Raises:
            ValueError: If format is invalid or not first line.
        """
        if line.startswith("nb_drones:"):
            splited = line.split(":")
            if len(splited) != 2:
                raise ValueError(f"Line {line_num}: Invalid drones format")

            val = splited[1].strip()
            try:
                parsed_drones = DroneParse(value=val)
            except ValidationError as e:
                raise ValueError(
                    f"Line {line_num}: Drone validation failed. Details: {e}"
                )
            self.drones = parsed_drones.value
            self.drones_line = True
        else:
            raise ValueError(f"Line {line_num}: File must start with nb_drones")

    def parse_zone(self, line: str, line_num: int) -> None:
        """Parse zone definition.

        Args:
            line: The zone line to parse.
            line_num: The line number (for error reporting).

        Raises:
            ValueError: If zone format is invalid or duplicate.
        """
        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if len(extract) != 4:
            raise ValueError(f"Line {line_num}: Invalid zone format")

        prefix = extract[0]
        start_flag = prefix == "start_hub:"
        end_flag = prefix == "end_hub:"

        try:
            metadata_obj = ZoneMetadata(**metadata_dict)
            zone = ZoneParse(
                name=extract[1],
                x=extract[2],
                y=extract[3],
                metadata=metadata_obj,
                is_start=start_flag,
                is_end=end_flag,
                zone_type=metadata_obj.zonetype,
            )
        except ValidationError as e:
            raise ValueError(
                f"Line {line_num}: Zone validation failed. Details: {e}"
            )

        if zone.name in self.zones:
            raise ValueError(
                f"Line {line_num}: Duplicate zone name '{zone.name}'"
            )

        if " " in zone.name or "-" in zone.name:
            raise ValueError(
                f"Line {line_num}: Zone name cannot contain spaces or dashes"
            )

        self.zones[zone.name] = zone

        if prefix == "start_hub:":
            if self.start_v is not None:
                raise ValueError(
                    f"Line {line_num}: Multiple start hubs found"
                )
            self.start_v = zone

        elif prefix == "end_hub:":
            if self.end_v is not None:
                raise ValueError(
                    f"Line {line_num}: Multiple end hubs found"
                )
            self.end_v = zone

    def parse_connection(self, line: str, line_num: int) -> None:
        """Parse connection definition.

        Args:
            line: The connection line to parse.
            line_num: The line number (for error reporting).

        Raises:
            ValueError: If connection format is invalid or duplicate.
        """
        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if len(extract) != 2:
            raise ValueError(f"Line {line_num}: Invalid connection format")

        parts = extract[1]

        if "-" not in parts:
            raise ValueError(
                f"Line {line_num}: Connection format invalid '{parts}'. "
                "Expected 'zone1-zone2'"
            )

        if parts.count("-") > 1:
            raise ValueError(
                f"Line {line_num}: Connection has multiple dashes"
            )

        zon1, zon2 = parts.split("-")

        if zon1 not in self.zones or zon2 not in self.zones:
            raise ValueError(
                f"Line {line_num}: Zone not found: {zon1} or {zon2}"
            )

        if zon1 == zon2:
            raise ValueError(
                f"Line {line_num}: Self-connection not allowed: {zon1}"
            )

        current_pair = frozenset({zon1, zon2})
        if current_pair in self.seen_connections:
            raise ValueError(
                f"Line {line_num}: Duplicate connection between {zon1}-{zon2}"
            )
        self.seen_connections.add(current_pair)

        try:
            metadata_obj = ConnectionMetadata(**metadata_dict)
            connection = ConnectionParse(
                from_zone=zon1, to_zone=zon2, metadata=metadata_obj
            )
        except ValidationError as e:
            raise ValueError(
                f"Line {line_num}: Connection validation failed. Details: {e}"
            )

        self.connections.append(connection)

    def read_file(self) -> None:
        """Read and parse the entire map configuration file.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If any parsing or validation fails.
        """
        with open(self.path_config, "r") as file:

            for line_num, line_content in enumerate(file, start=1):
                line = line_content.strip()

                # Skip comments and empty lines
                if line == "" or line.startswith("#"):
                    continue

                # Parse drone count (must be first)
                if not self.drones_line:
                    self.parse_drones(line, line_num)

                # Parse zones
                elif line.startswith(("hub:", "start_hub:", "end_hub:")):
                    self.parse_zone(line, line_num)

                # Parse connections
                elif line.startswith("connection:"):
                    self.parse_connection(line, line_num)

        # Validate file completeness
        if self.start_v is None or self.end_v is None:
            raise ValueError("Missing start_hub or end_hub in configuration")

        if not self.zones or not self.connections:
            raise ValueError("Map must have at least one zone and connection")
