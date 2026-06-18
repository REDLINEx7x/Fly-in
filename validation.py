from pydantic import BaseModel, Field
from enum import Enum
from typing import Any


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class DroneParse(BaseModel):

    value: int = Field(..., ge=1)


class ZoneParse(BaseModel):

    name: str = Field(..., min_length=1)
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    metadata: ZoneMetadata = Field(default_factory=ZoneMetadata)
    is_start: bool = False
    is_end: bool = False
    zone_type: ZoneType = Field(default=ZoneType.NORMAL)


class ConnectionParse(BaseModel):

    from_zone: str = Field(..., min_length=1)
    to_zone: str = Field(..., min_length=1)
    metadata: ConnectionMetadata = Field(default_factory=ConnectionMetadata)

class ZoneMetadata(BaseModel):

    zonetype: ZoneType = Field(default=ZoneType.NORMAL)
    color: str = Field(default=None)
    max_drones: int = Field(default=1, ge=1)


class ConnectionMetadata(BaseModel):

    max_link_capacity: int = Field(default=1, ge=1)

