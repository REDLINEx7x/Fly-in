"""Parser for drone simulation map configuration files.

Handles parsing and validation of map files containing zones, connections,
and drone count specifications according to subject requirements.
"""

from validation import (
    DroneParse,
    ZoneParse,
    ConnectionParse,
    ZoneType,
    ZoneMetadata,
    ConnectionMetadata,
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

    def extract_metadata(self, line: str, line_num: int) -> tuple[str, dict[str, str | int]]:
        """Extract metadata from bracketed section of a line."""
        match = re.search(r"\[(.*?)\]", line)
        clean_line = line
        metadata_dict: dict[str, str | int] = {}
        allowed_keys = {"color", "zone", "max_drones", "max_link_capacity"}

        if match:
            meta_data = match.group(1)
            clean_line = line.replace(match.group(0), "").strip()

            for item in meta_data.split():
                if "=" not in item:
                    raise ValueError(
                        f"Line {line_num}: Metadata format invalid for '{item}'. "
                        "Expected 'key=value'."
                    )

                if item.count("=") > 1:
                    raise ValueError(
                        f"Line {line_num}: Metadata format invalid for '{item}'. "
                        "Multiple equals signs not allowed."
                    )

                key, value = item.split("=", 1)
                if key in metadata_dict:
                    raise ValueError(
                        f"Line {line_num}: Duplicate metadata key '{key}'. Each key must appear only once."
                    )
                if key not in allowed_keys:
                    raise ValueError(
                        f"Line {line_num}: Unknown metadata key '{key}'. Valid keys are: {', '.join(sorted(allowed_keys))}."
                    )
                if key == "max_drones" or key == "max_link_capacity":
                    try:
                        metadata_dict[key] = int(value)
                    except ValueError:
                        raise ValueError(
                            f"Line {line_num}: '{key}' must be a valid integer."
                        )
                else:
                    metadata_dict[key] = value

        return clean_line, metadata_dict

    def parse_drones(self, line: str, line_num: int) -> None:
        """Parse drone count from first line."""
        if line.startswith("nb_drones:"):
            splited = line.split(":")
            if len(splited) != 2:
                raise ValueError(
                    f"Line {line_num}: Invalid format. Expected 'nb_drones: <number>'."
                )

            val = splited[1].strip()
            try:
                drone_count = int(val)
                parsed_drones = DroneParse(value=drone_count)
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: Drone count must be a valid positive integer."
                )
            except ValidationError:
                raise ValueError(
                    f"Line {line_num}: Drone count validation failed. Must be a valid positive integer."
                )

            self.drones = parsed_drones.value
            self.drones_line = True
        else:
            raise ValueError(f"Line {line_num}: File must start with 'nb_drones:'.")

    def parse_zone(self, line: str, line_num: int) -> None:
        """Parse zone definition."""
        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if len(extract) != 4:
            raise ValueError(
                f"Line {line_num}: Invalid zone format. Expected 4 tokens (type, name, x, y)."
            )

        prefix = extract[0]
        start_flag = prefix == "start_hub:"
        end_flag = prefix == "end_hub:"

        try:
            x_coord = int(extract[2])
            y_coord = int(extract[3])

            zone_type = None
            color = None
            max_drones = 1

            for key, value in metadata_dict.items():
                if key == "zone" and isinstance(value, str):
                    zone_type = ZoneType(value)
                elif key == "color" and isinstance(value, str):
                    color = value
                elif key == "max_drones" and isinstance(value, int):
                    max_drones = value

            metadata_obj = ZoneMetadata(
                zone=zone_type if zone_type else ZoneType.NORMAL,
                color=color,
                max_drones=max_drones
            )
            zone = ZoneParse(
                name=extract[1],
                x=x_coord,
                y=y_coord,
                metadata=metadata_obj,
                is_start=start_flag,
                is_end=end_flag,
                zone_type=metadata_obj.zone,
            )
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(
                    f"Line {line_num}: Zone coordinates must be valid integers."
                )
            raise ValueError(
                f"Line {line_num}: Zone validation failed. {e}"
            )
        except ValidationError:
            raise ValueError(
                f"Line {line_num}: Zone validation failed. Check coordinates, types, and metadata values."
            )

        if zone.name in self.zones:
            raise ValueError(f"Line {line_num}: Duplicate zone name '{zone.name}'.")

        if " " in zone.name or "-" in zone.name:
            raise ValueError(
                f"Line {line_num}: Zone name cannot contain spaces or dashes."
            )

        self.zones[zone.name] = zone

        if prefix == "start_hub:":
            if self.start_v is not None:
                raise ValueError(
                    f"Line {line_num}: Multiple start hubs found. Only one is allowed."
                )
            self.start_v = zone

        elif prefix == "end_hub:":
            if self.end_v is not None:
                raise ValueError(
                    f"Line {line_num}: Multiple end hubs found. Only one is allowed."
                )
            self.end_v = zone

    def parse_connection(self, line: str, line_num: int) -> None:
        """Parse connection definition."""
        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if len(extract) != 2:
            raise ValueError(f"Line {line_num}: Invalid connection format.")

        parts = extract[1]

        if "-" not in parts:
            raise ValueError(
                f"Line {line_num}: Connection format invalid '{parts}'. Expected 'zone1-zone2'."
            )

        if parts.count("-") > 1:
            raise ValueError(
                f"Line {line_num}: Connection contains multiple dashes. Only one is allowed."
            )

        zon1, zon2 = parts.split("-")

        if zon1 not in self.zones or zon2 not in self.zones:
            raise ValueError(
                f"Line {line_num}: Connection references an unknown zone ('{zon1}' or '{zon2}')."
            )

        if zon1 == zon2:
            raise ValueError(
                f"Line {line_num}: Self-connections are not allowed ('{zon1}')."
            )

        current_pair = frozenset({zon1, zon2})
        if current_pair in self.seen_connections:
            raise ValueError(
                f"Line {line_num}: Duplicate connection detected between '{zon1}' and '{zon2}'."
            )

        self.seen_connections.add(current_pair)

        try:
            max_link_capacity = 1

            for key, value in metadata_dict.items():
                if key == "max_link_capacity" and isinstance(value, int):
                    max_link_capacity = value

            metadata_obj = ConnectionMetadata(max_link_capacity=max_link_capacity)
            connection = ConnectionParse(
                from_zone=zon1, to_zone=zon2, metadata=metadata_obj
            )
        except ValidationError:
            # Removed {e}. Replaced with a clean, descriptive message.
            raise ValueError(
                f"Line {line_num}: Connection validation failed. Check metadata values (e.g., max_link_capacity)."
            )

        self.connections.append(connection)

    def read_file(self) -> None:
        """Read and parse the entire map configuration file."""
        with open(self.path_config, "r") as file:

            for line_num, line_content in enumerate(file, start=1):
                line = line_content.strip()

                if line == "" or line.startswith("#"):
                    continue
                if not self.drones_line:
                    self.parse_drones(line, line_num)

                elif line.startswith(("hub:", "start_hub:", "end_hub:")):
                    self.parse_zone(line, line_num)

                elif line.startswith("connection:"):
                    self.parse_connection(line, line_num)

                else:
                    raise ValueError(
                        f"Line {line_num}: Unrecognized configuration format."
                    )

        if self.start_v is None or self.end_v is None:
            raise ValueError(
                "Invalid Map: Missing 'start_hub' or 'end_hub' in the configuration."
            )

        if not self.zones or not self.connections:
            raise ValueError(
                "Invalid Map: Configuration must have at least one zone and one connection."
            )
