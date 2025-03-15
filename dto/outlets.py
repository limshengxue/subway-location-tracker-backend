from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class OverlappingOutletDTO(BaseModel):
    id: str
    name: str

class OverlappingOutletsDTO(BaseModel):
    id: int 
    distance: float
    outlet1: OverlappingOutletDTO 
    outlet2: OverlappingOutletDTO

class OutletDTO(BaseModel):
    id: str 
    name: str  
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: float
    operating_hours: Optional[str] = None
    waze_link: str 
    all_overlapping: List[OverlappingOutletsDTO] = []

class OutletInfoDTO(BaseModel):
    outlets: List[OutletDTO]
    last_updated: datetime

