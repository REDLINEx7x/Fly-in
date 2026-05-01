from pydantic import BaseModel, Field
from typing import Optional, Any
from models import DroneParse, ZoneParse, ConnectionParse
import re

class Parser:
    def __init__(self, file_path : str):
        self.path_config = file_path
        self.drones: int = 0
        self.zones: dict[str, ZoneParse] = {}
        self.connections: list[ConnectionParse] = []
        self.start_v: Optional[ZoneParse] = None
        self.end_v: Optional[ZoneParse] = None
        self.drones_line = False

    def read_file(self):
        with open(self.path_config, "r") as file:

            for l in file:
                line = l.strip()
                if line == "" or line.startswith("#"):
                    continue
                if not self.drones_line:
                    if line.startswith("nb_drones:"):
                        splited = line.split(':')
                        val = splited[1].strip()
                        parsed_drones = DroneParse(value=val)
                        self.drones = parsed_drones.value
                        self.drones_line = True
                    else:
                        raise ValueError("File must start with nb_drones")
                elif line.startswith(("hub:", "start_hub:", "end_hub:")):

                        match = re.search(r"\[(.*?)\]", line)
                        clean_line = line
                        metadata_dict = {}
                        if match:
                            meta_data = match.group(1)
                            clean_line = line.replace(match.group(0), "").strip()
                            metadata_dict = {
                                item.split('=')[0]: item.split('=')[1]
                                for item in meta_data.split() if "=" in item
                                }
                        else:
                            line = clean_line
                            metadata_dict = {}

                        extract = clean_line.split()
                        if not len(extract) == 4:
                            raise ValueError("zone info are false")
                        try:
                            prefix = extract[0]
                            start_flag = (prefix == "start_hub:")
                            end_flag = (prefix == "end_hub:")
                            zone = ZoneParse(name=extract[1], x=extract[2], y=extract[3], metadata=metadata_dict, is_start=start_flag, is_end=end_flag)

                            if zone.name in self.zones:
                                raise ValueError(f"Duplicate zone name: {zone.name}")

                            self.zones[zone.name] = zone

                            if prefix == "start_hub:":
                                if self.start_v is not None:
                                    raise ValueError("Multiple start hubs found!")
                                self.start_v = zone

                            elif prefix == "end_hub:":
                                if self.end_v is not None:
                                    raise ValueError("Multiple end hubs found!")
                                self.end_v = zone
                        except ValueError as e:
                            print(e)
                elif line.startswith("connection:"):

                    match = re.search(r"\[(.*?)\]", line)
                    clean_line = line
                    metadata_dict = {}
                    if match:
                        meta_data = match.group(1)
                        clean_line = line.replace(match.group(0), "").strip()
                        metadata_dict = {
                            item.split('=')[0]: item.split('=')[1]
                            for item in meta_data.split() if "=" in item
                        }
                    extract = clean_line.split()
                    if len(extract) != 2:
                        raise ValueError("few info")
                    parts = extract[1]
                    if '-' not in parts:
                        raise ValueError(f"Invalid connection format: {parts}. Expected 'zone1-zone2'")
                    zon1, zon2 = parts.split('-')
                    if zon1 not in self.zones or zon2 not in self.zones:
                        raise ValueError(f"One or both zones not found: {zon1}, {zon2}")
                    if zon1 == zon2:
                        raise ValueError(f"Self-connection detected: {zon1}")
                    try:
                        connection = ConnectionParse(
                            from_zone=zon1,
                            to_zone=zon2,
                            metadata=metadata_dict
                        )
                        self.connections.append(connection)
                    except ValueError as e:
                        print(e)
