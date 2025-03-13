from sqlmodel import TEXT, Column, SQLModel, Field
from typing import Optional

class Outlet(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str  = Field(sa_column=Column(TEXT))
    address: Optional[str]  = Field(default=None, sa_column=Column(TEXT, nullable=True))
    latitude: Optional[float]
    longitude: float
    operating_hours: Optional[str] = Field(default=None)
    waze_link: str  = Field(sa_column=Column(TEXT))
