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
