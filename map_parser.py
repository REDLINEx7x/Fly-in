from validation import (
    DroneParse, ZoneParse, ConnectionParse, ZoneType,
    ZoneMetadata, ConnectionMetadata,
)
from pydantic import ValidationError
from typing import Optional, Any
import re


class Parser:
    def __init__(self, file_path: str):
        self.path_config = file_path
        self.drones: int = 0
        self.zones: dict[str, ZoneParse] = {}
        self.connections: list[ConnectionParse] = []
        self.seen_connections: set[frozenset[str]] = set()
        self.start_v: Optional[ZoneParse] = None
        self.end_v: Optional[ZoneParse] = None
        self.drones_line = False

    def extract_metadata(self, line: str, line_num : int):

        match = re.search(r"\[(.*?)\]", line)
        clean_line = line
        metadata_dict = {}

        if match:
            meta_data = match.group(1)
            clean_line = line.replace(match.group(0), "").strip()

            for item in meta_data.split():
                if "=" not in item:
                    raise ValueError(f"Metadata format is not valid for item: '{item}'. Expected 'key=value'.")

                key, value = item.split("=", 1)
                metadata_dict[key] = value

        return clean_line, metadata_dict

    def parse_drones(self, line: str, line_num: int):

        if line.startswith("nb_drones:"):
            splited = line.split(":")
            if not len(splited) == 2:
                raise ValueError(f"Line {line_num} invalid drones format")

            val = splited[1].strip()
            try:
                parsed_drones = DroneParse(value=val)
            except ValidationError as e:
                raise ValueError(f"Line {line_num}: Drone validation failed. Details: {e}")
            self.drones = parsed_drones.value
            self.drones_line = True
        else:
            raise ValueError(f"line {line_num} File must start with nb_drones")

    def parse_zone(self, line: str, line_num: int):

        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if not len(extract) == 4:
            raise ValueError(f"line {line_num}: invalid zone")

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
                zone_type=metadata_obj.zonetype
            )
        except ValidationError as e:
            raise ValueError(f"Line {line_num}: Zone validation failed. Details: {e}")
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone name: {zone.name} in line {line_num}")
        if " " in zone.name or "-" in zone.name:
            raise ValueError(f"line {line_num}: invalid zone name")

        self.zones[zone.name] = zone

        if prefix == "start_hub:":
            if self.start_v is not None:
                raise ValueError(f"line {line_num} Multiple start hubs found!")

            self.start_v = zone

        elif prefix == "end_hub:":
            if self.end_v is not None:
                raise ValueError(f"line {line_num} Multiple end hubs found!")

            self.end_v = zone

    def parse_connection(self, line: str, line_num):

        clean_line, metadata_dict = self.extract_metadata(line, line_num)

        extract = clean_line.split()

        if len(extract) != 2:
            raise ValueError(f"Line {line_num} invalid connection format")

        parts = extract[1]

        if "-" not in parts:
            raise ValueError(
                f"Invalid connection format: {parts}. Expected 'zone1-zone2'"
            )
        if parts.count("-") > 1:
            raise ValueError(f"Line {line_num} invalid connection format")
        zon1, zon2 = parts.split("-")

        if zon1 not in self.zones or zon2 not in self.zones:
            raise ValueError(
                f"line {line_num} One or both zones not found: {zon1}, {zon2}"
            )

        if zon1 == zon2:
            raise ValueError(f"line {line_num} self-connection detected: {zon1}")

        current_pair = frozenset({zon1, zon2})
        if current_pair in self.seen_connections:
            raise ValueError(f"Line {line_num}: Duplicate connection found between {zon1} and {zon2}")
        else:
            self.seen_connections.add(current_pair)
        try:
            metadata_obj = ConnectionMetadata(**metadata_dict)
            connection = ConnectionParse(
            from_zone=zon1, to_zone=zon2, metadata=metadata_obj
            )
        except ValidationError as e:
            raise ValueError(f"Line {line_num}: Connection validation failed. Details: {e}")

        self.connections.append(connection)

    def read_file(self):

        with open(self.path_config, "r") as file:

            for line_num, l in enumerate(file, start=1):

                line = l.strip()

                if line == "" or line.startswith("#"):
                    continue

                if not self.drones_line:
                    self.parse_drones(line, line_num)

                elif line.startswith(("hub:", "start_hub:", "end_hub:")):
                    self.parse_zone(line, line_num)

                elif line.startswith("connection:"):
                    self.parse_connection(line, line_num)

            if self.start_v is None or self.end_v is None:
                raise ValueError("Missing start or end hub")
            if not (self.start_v and self.end_v):
                raise ValueError("Invalid start/end configuration")
