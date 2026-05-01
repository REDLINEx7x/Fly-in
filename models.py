from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum

class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

class DroneParse(BaseModel):

    value: int = Field (..., ge=1)


class ZoneParse(BaseModel):

    name: str = Field(..., min_length=1)
    x: int = Field(...)
    y: int = Field(...)
    metadata: dict[str, str] = Field(default_factory=dict)
    is_start: bool = False
    is_end: bool = False

class ConnectionParse(BaseModel):

    from_zone: str = Field(..., min_length=1)
    to_zone: str = Field(..., min_length=1 )
    metadata: dict[str, str] = Field(default_factory=dict)
