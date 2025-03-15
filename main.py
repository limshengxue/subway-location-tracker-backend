from fastapi import Depends, FastAPI, BackgroundTasks
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from data_ingest.ingester import ingest_data
from db import get_db, get_session, engine
from models.models import Outlet, LatestUpdatedTimestamp
from dto.outlets import OutletInfoDTO

scheduler = BackgroundScheduler()

def should_ingest(session: Session) -> bool:
    """Check if ingest_data should be triggered based on timestamp."""
    record = session.exec(select(LatestUpdatedTimestamp).order_by(LatestUpdatedTimestamp.timestamp.desc())).first()
    if not record or (datetime.utcnow() - datetime.fromisoformat(record.timestamp)) > timedelta(hours=24):
        return True
    return False

def schedule_job():
    scheduler.add_job(
        ingest_data,
        IntervalTrigger(hours=24),  # Run every 24 hours
        id="scrape_subway_outlet_data",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started...")
            
async def app_lifespan(app: FastAPI):
    # Initialize the database
    get_db() 
    # Run the scheduler when the app starts
    with Session(engine) as session:
        if should_ingest(session): # Start an initial ingestion if it hasn't been done in the last 24 hours
            ingest_data()
        schedule_job()
    yield  
    # Shut down the scheduler when the app is shutting down
    scheduler.shutdown() 
    print("Scheduler shut down...")

# Define app
app = FastAPI(lifespan=app_lifespan)

@app.get("/outlets")
async def get_outlets(session: Session = Depends(get_session)) -> OutletInfoDTO:
    outlets = session.exec(select(Outlet)).all()
    latest_updated_timestamp = session.exec(select(LatestUpdatedTimestamp)).first()

    return {
        "outlets": outlets,
        "last_updated": latest_updated_timestamp.timestamp if latest_updated_timestamp else None
    }
    
