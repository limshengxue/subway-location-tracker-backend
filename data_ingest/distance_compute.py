import numpy as np
import pandas as pd
from geopy.distance import geodesic
from typing import List
from models.models import Outlet, OverlappingOutlet

def compute_distance_matrix(outlets: List[Outlet]):
    # Create a sorted list of unique outlet IDs
    outlet_ids = [outlet.id for outlet in outlets]
    
    # Initialize an empty DataFrame for the distance matrix
    distance_matrix = pd.DataFrame(0.0, index=outlet_ids, columns=outlet_ids)
    overlapping_outlets = []
    
    for i, outlet1 in enumerate(outlets):
        for j, outlet2 in enumerate(outlets):
            if i < j:  # Only upper triangle
                coord1 = (outlet1.latitude, outlet1.longitude)
                coord2 = (outlet2.latitude, outlet2.longitude)
                
                distance = geodesic(coord1, coord2).kilometers
                
                # Store in DataFrame (symmetric)
                distance_matrix.at[outlet1.id, outlet2.id] = distance
                distance_matrix.at[outlet2.id, outlet1.id] = distance
                
                if distance < 5.0:
                    overlapping_outlets.append(
                        OverlappingOutlet(
                            outlet1_id=outlet1.id,
                            outlet2_id=outlet2.id,
                            distance=distance
                        )
                    )
    
    return distance_matrix, overlapping_outlets
