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
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_start: bool = False
    is_end: bool = False
    zone_type: ZoneType = Field(default=ZoneType.NORMAL)


class ConnectionParse(BaseModel):

    from_zone: str = Field(..., min_length=1)
    to_zone: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
