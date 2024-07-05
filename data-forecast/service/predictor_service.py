from datetime import datetime, timedelta
import sys
import os
import pandas as pd
import threading
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import model_training, model_predictor, shared

# Global variable to store Trace_Object instances
trace_objects = {}
leaderboard_entries = []
last_execution_time = None
trace_dir_drive = "dataset_traces/"
trained_traces = [] 

# Helper function to fill missing minutes with zeros
def fill_missing_minutes(trace_obj, last_timestamp, new_timestamp):
    time_format = '%Y-%m-%d %H:%M:%S'

    current_time = datetime.strptime(str(last_timestamp), time_format) + timedelta(minutes=1)
    new_time = datetime.strptime(new_timestamp, time_format)
    
    while current_time < new_time:
        new_entry = pd.DataFrame({
            'level_0': [len(trace_obj.raw_trace)],
            'item_id': [trace_obj.trace_id],
            'timestamp': [pd.to_datetime( current_time.strftime(time_format) )],
            'target': [0]
        })
        trace_obj.raw_trace = pd.concat([trace_obj.raw_trace, new_entry], ignore_index=True)
        current_time += timedelta(minutes=1)

def remove_trace(trace_id):
    global trace_objects

    if trace_id in trace_objects:
        del trace_objects[trace_id]
        #print(f"Trace ID {trace_id} removed from trace_objects.")
    else:
        print(f"Trace ID {trace_id} does not exist in trace_objects.")


# Function to add entries to a Trace_Object, this assumes that each entry is one minute interval
def add_trace_entry(timestamp, trace_id, invocation_count, invocation_duration, memory_used_invocation, compilation_cost):
    global trace_objects
    
    # Adjust the timestamp to have seconds as "00", just in case there are seconds
    timestamp = timestamp[:16] + ":00"

    # If trace_id is not in trace_objects, create a new Trace_Object
    if trace_id not in trace_objects:
        trace_objects[trace_id] = shared.Trace_Object(trace_id=trace_id)
    
    # Get the corresponding Trace_Object
    trace_obj = trace_objects[trace_id]
    
    # Fill missing minutes with zeroes if there are previous entries
    if not trace_obj.raw_trace.empty:
        last_timestamp = trace_obj.raw_trace.iloc[-1]['timestamp']
        fill_missing_minutes(trace_obj, last_timestamp, timestamp)

    # Check if the timestamp already exists in raw_trace
    if trace_obj.raw_trace.size > 0 and pd.to_datetime(timestamp) in trace_obj.raw_trace['timestamp'].values:
        # Update the existing entry
        trace_obj.raw_trace.loc[trace_obj.raw_trace['timestamp'] == timestamp, 'target'] += invocation_count
    else:
        # Create a DataFrame for the new entry
        new_entry = pd.DataFrame({
            'level_0': [len(trace_obj.raw_trace)],
            'item_id': [trace_id],
            'timestamp': [pd.to_datetime(timestamp)],
            'target': [invocation_count]
        })
        
        # Add the new entry to raw_trace
        trace_obj.raw_trace = pd.concat([trace_obj.raw_trace, new_entry], ignore_index=True)
    
    trace_obj.trace_id = trace_id
    trace_obj.invocation_duration = invocation_duration
    trace_obj.memory_used_invocation = memory_used_invocation
    trace_obj.compilation_cost = compilation_cost
    
    #print("...debug...")
    #print(trace_objects)


# Define the function outside of compute_leaderboard
def process_trace(trace_id, trace_objects, trained_traces, trace_dir_drive, new_leaderboard, leaderboard_lock):
    # Get forecast using model predictor
    prediction = model_predictor.get_trace_forecast(trace_id, trace_objects[trace_id], trained_traces, trace_dir_drive, debug=False, log=True, output_dir="data-forecast/predictor/log_results/")
    
    cost = model_predictor.get_normal_cost(trace_id, prediction)
    
    # Append to leaderboard entries in a thread-safe manner
    with leaderboard_lock:
        new_leaderboard.append({"trace_id": trace_id, "cost": cost})

def compute_leaderboard():
    global leaderboard_entries, trained_traces, trace_objects, trace_dir_drive
    print("** computing leaderboard **")

    # Use Manager to create a list and a lock that can be shared between processes
    manager = multiprocessing.Manager()
    new_leaderboard = manager.list()
    leaderboard_lock = manager.Lock()

    # Use ProcessPoolExecutor to process each trace_id in a separate process
    with ProcessPoolExecutor(max_workers=None) as executor:
        futures = [executor.submit(process_trace, trace_id, trace_objects, trained_traces, trace_dir_drive, new_leaderboard, leaderboard_lock) for trace_id in trace_objects]

        # Ensure all processes complete
        for future in futures:
            future.result()
        
        executor.shutdown(wait=False)  # Explicitly shut down the executor

    # Sort leaderboard entries by cost in descending order
    new_leaderboard = sorted(new_leaderboard, key=lambda x: x["cost"], reverse=True)
    
    leaderboard_entries = list(new_leaderboard)
    
    print("LOG: flush logs", flush=True)


def leaderboard_routine():
    """Function to run compute_leaderboard() every 10 minutes."""
    global last_execution_time
    #routine_sleep = 600 # Wait for 10 minutes (600 seconds) before running again
    
    #while True:
        
    #    if last_execution_time is None or (datetime.now() - last_execution_time) > timedelta(seconds=routine_sleep):
    #        compute_leaderboard()
    #        last_execution_time = datetime.now()
            
    #    time.sleep( (timedelta(seconds=routine_sleep) - (datetime.now() - last_execution_time)).total_seconds() )


def init():
    global trained_traces, trace_dir_drive

    #model_training.shared.simulation_configuration #if I want to define some  configurations, this is the place
    #model_predictor.shared.simulation_configuration #if I want to define some  configurations, this is the place
    
    trace_dir_drive = "dataset_traces/" # this iss for  debuging
    trained_traces = model_training.load_trained_traces()

    leaderboard_thread = threading.Thread(target=leaderboard_routine)
    leaderboard_thread.daemon = True  # Set the thread as a daemon so it will terminate when the main program ends
    leaderboard_thread.start()

