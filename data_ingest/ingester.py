import os
import numpy as np
from sqlmodel import Session, select, text

from data_ingest.distance_compute import compute_distance_matrix
from .scrapper import scrape_data
from db import get_db, engine
from models.models import LatestUpdatedTimestamp

def ingest_data():
    # Get session
    get_db() # TODO: Remove this line, place in startup of web server

    # Scrape data
    results = scrape_data()
    
    # Compute Additional Attributes
    distance_matrix, overlapping_outlets = compute_distance_matrix(results)

    # Persist Data
    with Session(engine) as session:
        # Remove existing data
        session.exec(text('DELETE FROM outlet'))
        session.exec(text('DELETE FROM overlappingoutlet'))
        
        # Add new data
        session.add_all(results)
        session.add_all(overlapping_outlets)

        # Update the latest updated_at timestamp
        latest_updated_timestamp = session.exec(select(LatestUpdatedTimestamp)).first()
        if latest_updated_timestamp is None:
            latest_updated_timestamp = LatestUpdatedTimestamp(timestamp=str(np.datetime64('now')))
            session.add(latest_updated_timestamp)
        else:
            latest_updated_timestamp.timestamp = str(np.datetime64('now'))

        session.commit()

        # Persist the numpy matrix
        file_path = os.getenv("DISTANCE_MATRIX_FILE_PATH")
        distance_matrix.to_csv(file_path)



