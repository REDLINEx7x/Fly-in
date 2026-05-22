from pydantic import BaseModel, Field
from typing import Optional, Any
from validation import DroneParse, ZoneParse, ConnectionParse, ZoneType
import re


class Parser:
    def __init__(self, file_path: str):
        self.path_config = file_path
        self.drones: int = 0
        self.zones: dict[str, ZoneParse] = {}
        self.connections: list[ConnectionParse] = []
        self.start_v: Optional[ZoneParse] = None
        self.end_v: Optional[ZoneParse] = None
        self.drones_line = False

    def extract_metadata(self, line: str):

        match = re.search(r"\[(.*?)\]", line)
        clean_line = line
        metadata_dict = {}

        if match:
            meta_data = match.group(1)
            clean_line = line.replace(match.group(0), "").strip()

            metadata_dict = {
                item.split("=")[0]: item.split("=")[1]
                for item in meta_data.split()
                if "=" in item
            }

        return clean_line, metadata_dict

    def parse_drones(self, line: str, line_num: int):

        if line.startswith("nb_drones:"):
            splited = line.split(":")
            val = splited[1].strip()
            parsed_drones = DroneParse(value=val)
            self.drones = parsed_drones.value
            self.drones_line = True
        else:
            raise ValueError(f"line {line_num} File must start with nb_drones")

    def parse_zone(self, line: str, line_num: int):

        clean_line, metadata_dict = self.extract_metadata(line)

        extract = clean_line.split()

        if not len(extract) == 4:
            raise ValueError(f"line {line_num}: invalid zone")

        prefix = extract[0]
        start_flag = prefix == "start_hub:"
        end_flag = prefix == "end_hub:"

        z_type = metadata_dict.get("zone", "normal")
        zone = ZoneParse(
            name=extract[1],
            x=extract[2],
            y=extract[3],
            metadata=metadata_dict,
            is_start=start_flag,
            is_end=end_flag,
            zone_type=ZoneType(z_type),
        )
        # print(zone.zone_type.value)

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

        clean_line, metadata_dict = self.extract_metadata(line)

        extract = clean_line.split()

        if len(extract) != 2:
            raise ValueError(f"line {line_num} invalid connection format")

        parts = extract[1]

        if "-" not in parts:
            raise ValueError(
                f"Invalid connection format: {parts}. Expected 'zone1-zone2'"
            )

        zon1, zon2 = parts.split("-")

        if zon1 not in self.zones or zon2 not in self.zones:
            raise ValueError(
                f"line {line_num} One or both zones not found: {zon1}, {zon2}"
            )

        if zon1 == zon2:
            raise ValueError(f"line {line_num} self-connection detected: {zon1}")

        connection = ConnectionParse(
            from_zone=zon1, to_zone=zon2, metadata=metadata_dict
        )

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
