from datetime import datetime
import os
from sqlmodel import Session, select, text

from data_ingest.distance_compute import compute_distance_matrix
from data_ingest.preprocess_op_hours import preprocess_op_hours
from .scrapper import scrape_data
from db import engine
from models.models import LatestUpdatedTimestamp

def ingest_data():
    # Scrape data
    results = scrape_data()
    
    # Compute Additional Attributes
    distance_matrix, overlapping_outlets = compute_distance_matrix(results)
    outlets_operating_hours = preprocess_op_hours(results)

    # Persist Data
    with Session(engine) as session:
        # Remove existing data
        session.exec(text('DELETE FROM overlappingoutlet'))
        session.exec(text('DELETE FROM outletoperatinghours'))
        session.exec(text('DELETE FROM outlet'))
        
        # Add new data
        session.add_all(results)
        session.add_all(overlapping_outlets)
        session.add_all(outlets_operating_hours)

        # Update the latest updated_at timestamp
        latest_updated_timestamp = session.exec(select(LatestUpdatedTimestamp)).first()
        if latest_updated_timestamp is None:
            latest_updated_timestamp = LatestUpdatedTimestamp(timestamp=datetime.now().isoformat())
            session.add(latest_updated_timestamp)
        else:
            latest_updated_timestamp.timestamp = datetime.now().isoformat()

        session.commit()

        # Persist the df matrix
        file_path = os.getenv("DISTANCE_MATRIX_FILE_PATH")
        distance_matrix.to_csv(file_path)



