from sqlmodel import Session
from .scrapper import scrape_data
from db import get_db, engine

def ingest_data():
    # Get session
    get_db() # TODO: Remove this line, place in startup of web server

    # Scrape data
    results = scrape_data()
    
    # Compute Additional Attributes
    ## Distance Matrix

    ## Detect 5 KM Overlap

    # Persist Data
    with Session(engine) as session:
        session.add_all(results)
        session.commit()



