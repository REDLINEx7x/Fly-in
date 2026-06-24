from pydantic import BaseModel, Field
from enum import Enum


class ZoneType(str, Enum):
    """Enumeration of zone types."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ZoneMetadata(BaseModel):
    """Metadata for zone configuration."""

    zonetype: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1, ge=1)


class ConnectionMetadata(BaseModel):
    """Metadata for connection configuration."""

    max_link_capacity: int = Field(default=1, )


class DroneParse(BaseModel):
    """Drone count validation model."""

    value: int = Field(..., ge=1)


class ZoneParse(BaseModel):
    """Zone validation model."""

    name: str = Field(..., min_length=1)
    x: int = Field(...)  # Valid integer (can be negative)
    y: int = Field(...)  # Valid integer (can be negative)
    metadata: ZoneMetadata = Field(default_factory=ZoneMetadata)
    is_start: bool = False
    is_end: bool = False
    zone_type: ZoneType = Field(default=ZoneType.NORMAL)


class ConnectionParse(BaseModel):
    """Connection validation model."""

    from_zone: str = Field(..., min_length=1)
    to_zone: str = Field(..., min_length=1)
    metadata: ConnectionMetadata = Field(default_factory=ConnectionMetadata)

