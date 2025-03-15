from models.models import Outlet, OutletOperatingHours
from llm.preprocess_data import OutletOperatingHoursDescription, preprocess_data
from langchain_core.runnables import RunnableParallel, RunnableLambda
from datetime import time

def batching_outlets(outlets: list[Outlet]):
    batches = []
    # split the outlets into 50 per batch
    for i in range(0, len(outlets), 50):
        batch = outlets[i:i+50]
        outlet_op_hours = [OutletOperatingHoursDescription(outlet_id=outlet.id, operating_hours=outlet.operating_hours) for outlet in batch]
        batches.append(outlet_op_hours)

    return batches

from langchain.schema.runnable import RunnableLambda, RunnableParallel

def preprocess_op_hours(outlets: list[Outlet]) -> list[OutletOperatingHours]:
    batches = batching_outlets(outlets)
    jobs = {}

    for i, batch in enumerate(batches):
        runnable = RunnableLambda(lambda x, batch=batch: preprocess_data(batch))
        jobs[f"batch{i}"] = runnable  # Store the runnable in the dictionary

    # Parallel execution of jobs
    parallel_processing_chain = RunnableParallel(jobs)
    
    # Invoke the parallel chain
    batch_results = parallel_processing_chain.invoke({})

    # Postprocess: Flatten the batch results into a single list
    all_records = []
    for batch in batch_results.values():
        all_records.extend(batch)  # Append all records from each batch

    # parse the record to 
    return [OutletOperatingHours(
            outlet_id=record.outlet_id,
            mon_open=time.fromisoformat(record.mon_open) if record.mon_open else None,
            mon_close=time.fromisoformat(record.mon_close) if record.mon_close else None,
            tue_open=time.fromisoformat(record.tue_open) if record.tue_open else None,
            tue_close=time.fromisoformat(record.tue_close) if record.tue_close else None,
            wed_open=time.fromisoformat(record.wed_open) if record.wed_open else None,
            wed_close=time.fromisoformat(record.wed_close) if record.wed_close else None,
            thu_open=time.fromisoformat(record.thu_open) if record.thu_open else None,
            thu_close=time.fromisoformat(record.thu_close) if record.thu_close else None,
            fri_open=time.fromisoformat(record.fri_open) if record.fri_open else None,
            fri_close=time.fromisoformat(record.fri_close) if record.fri_close else None,
            sat_open=time.fromisoformat(record.sat_open) if record.sat_open else None,
            sat_close=time.fromisoformat(record.sat_close) if record.sat_close else None,
            sun_open=time.fromisoformat(record.sun_open) if record.sun_open else None,
            sun_close=time.fromisoformat(record.sun_close) if record.sun_close else None,
            public_holiday_open=time.fromisoformat(record.public_holiday_open) if record.public_holiday_open else None,
            public_holiday_close=time.fromisoformat(record.public_holiday_close) if record.public_holiday_close else None,
        ) for record in all_records]



    