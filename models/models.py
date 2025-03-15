from datetime import time as dt_time
from sqlmodel import TEXT, Column, Relationship, SQLModel, Field
from typing import List, Optional

class Outlet(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str  = Field(sa_column=Column(TEXT))
    address: Optional[str]  = Field(default=None, sa_column=Column(TEXT, nullable=True))
    latitude: Optional[float]
    longitude: float
    operating_hours: Optional[str] = Field(default=None)
    waze_link: str  = Field(sa_column=Column(TEXT))

    overlapping_as_outlet1: List["OverlappingOutlet"] = Relationship(
        back_populates="outlet1",
        sa_relationship_kwargs={"foreign_keys": "[OverlappingOutlet.outlet1_id]"}
    )
    
    overlapping_as_outlet2: List["OverlappingOutlet"] = Relationship(
        back_populates="outlet2",
        sa_relationship_kwargs={"foreign_keys": "[OverlappingOutlet.outlet2_id]"}
    )
    
    # Property to get all overlapping outlets
    @property
    def all_overlapping(self) -> List["OverlappingOutlet"]:
        return self.overlapping_as_outlet1 + self.overlapping_as_outlet2

    operating_hours_list: List["OutletOperatingHours"] = Relationship(
        back_populates="outlet",
        sa_relationship_kwargs={"foreign_keys": "[OutletOperatingHours.outlet_id]"}
    )


class OverlappingOutlet(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  
    outlet1_id: str = Field(foreign_key="outlet.id")
    outlet2_id: str = Field(foreign_key="outlet.id")
    distance: float

   # Define the reverse relationships
    outlet1: "Outlet" = Relationship(
        back_populates="overlapping_as_outlet1",
        sa_relationship_kwargs={"foreign_keys": "OverlappingOutlet.outlet1_id"}
    )
    
    outlet2: "Outlet" = Relationship(
        back_populates="overlapping_as_outlet2",
        sa_relationship_kwargs={"foreign_keys": "OverlappingOutlet.outlet2_id"}
    )
    
class LatestUpdatedTimestamp(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  
    timestamp: str

class OutletOperatingHours(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    outlet_id: str = Field(foreign_key="outlet.id")
    
    outlet: "Outlet" = Relationship(
        back_populates="operating_hours_list",
        sa_relationship_kwargs={"foreign_keys": "OutletOperatingHours.outlet_id"}
    )

    mon_open: dt_time | None = Field(None, description="Monday opening time (HH:MM format)")
    mon_close: dt_time | None = Field(None, description="Monday closing time (HH:MM format)")
    tue_open: dt_time | None = Field(None, description="Tuesday opening time (HH:MM format)")
    tue_close: dt_time | None = Field(None, description="Tuesday closing time (HH:MM format)")
    wed_open: dt_time | None = Field(None, description="Wednesday opening time (HH:MM format)")
    wed_close: dt_time | None = Field(None, description="Wednesday closing time (HH:MM format)")
    thu_open: dt_time | None = Field(None, description="Thursday opening time (HH:MM format)")
    thu_close: dt_time | None = Field(None, description="Thursday closing time (HH:MM format)")
    fri_open: dt_time | None = Field(None, description="Friday opening time (HH:MM format)")
    fri_close: dt_time | None = Field(None, description="Friday closing time (HH:MM format)")
    sat_open: dt_time | None = Field(None, description="Saturday opening time (HH:MM format)")
    sat_close: dt_time | None = Field(None, description="Saturday closing time (HH:MM format)")
    sun_open: dt_time | None = Field(None, description="Sunday opening time (HH:MM format)")
    sun_close: dt_time | None = Field(None, description="Sunday closing time (HH:MM format)")
    public_holiday_open: dt_time | None = Field(None, description="Public holiday opening time (HH:MM format)")
    public_holiday_close: dt_time | None = Field(None, description="Public holiday closing time (HH:MM format)")

