from fastapi import Depends, FastAPI
from sqlmodel import Session, select
from data_ingest.ingester import ingest_data
import os
from db import get_session
from models.models import Outlet 
from dto.outlets import OutletDTO

app = FastAPI()


@app.get("/outlets")
async def get_outlets(session: Session = Depends(get_session)) -> list[OutletDTO]:
    outlets = session.exec(select(Outlet)).all()
    return outlets