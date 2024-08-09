from datetime import datetime, timedelta
import sys
import os
import pandas as pd
import pickle
import shutil
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
from io import StringIO  

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import shared

# Global variable to store Trace_Object instances
trace_objects = {}
leaderboard_entries = {}
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
        #print(f"Trace ID {trace_id} removed from trace_objects.", flush=True) 
    else:
        print(f"Trace ID {trace_id} does not exist in trace_objects.", flush=True)


# Function to add entries to a Trace_Object, this assumes that each entry is one minute interval
def add_point_trace_entry(timestamp, trace_id, invocation_count, invocation_duration, memory_used_invocation, compilation_cost):
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

# Function to add entries to a Trace_Object, this assumes that each entry is one minute interval
def add_dataframe_trace_entry(trace_id, new_df, invocation_duration, memory_used_invocation, compilation_cost):
    global trace_objects
    
    new_df = pd.read_json( StringIO(new_df), orient='records')
    #print(new_df, flush=True)

    # If trace_id is not in trace_objects, create a new Trace_Object
    if trace_id not in trace_objects:
        trace_objects[trace_id] = shared.Trace_Object(trace_id=trace_id)
    
    # Get the corresponding Trace_Object
    trace_obj = trace_objects[trace_id]
    
    # Fill missing minutes with zeroes if there are previous entries
    if trace_obj.raw_trace.empty:
        trace_obj.raw_trace = new_df
        trace_obj.trace_id = trace_id
        trace_obj.invocation_duration = invocation_duration
        trace_obj.memory_used_invocation = memory_used_invocation
        trace_obj.compilation_cost = compilation_cost

        return

    combined_raw_trace = pd.concat([trace_obj.raw_trace, new_df], ignore_index=True)

    min_timestamp = combined_raw_trace['timestamp'].min()
    max_timestamp = combined_raw_trace['timestamp'].max()

    all_minutes = pd.date_range(start=min_timestamp, end=max_timestamp, freq='min')
    all_minutes_df = pd.DataFrame({'timestamp': all_minutes})

    all_minutes_df['item_id'] = trace_id

    merged_df = pd.merge(all_minutes_df, combined_raw_trace, on=['timestamp', 'item_id'], how='left').fillna({'target': 0})

    result = merged_df.groupby(['timestamp', 'item_id']).agg({
        'target': 'sum',
    }).reset_index()

    trace_obj.raw_trace = result


def run_predictor_process(work, idx, return_dict):

    print(f"Hi from process idx {idx}", flush=True)

    work_dir = f"running_traces/process_{idx}"
    traces_dir = f"{work_dir}/traces"
    models_dir = f"{work_dir}/autogluon_models"
    os.makedirs(traces_dir, exist_ok=True)
    shutil.copytree('../predictor/autogluon_models', models_dir, dirs_exist_ok=True)

    start_time = time.time()

    with open(f"{traces_dir}/work_{idx}", 'wb') as f:
        pickle.dump(work, f)

    end_time = time.time()
    print(f"LOG: storing traces took {end_time - start_time:.4f} seconds")


    start_time = time.time()
    #result = subprocess.run(["python3", "predictor_bridge.py", work_dir, traces_dir, models_dir, str(idx)], capture_output=True, text=True)
    
    docker_command = [
        "docker", "run", "--rm", "--gpus", "all", "--network", "host", 
        "-v", "/home/claudiocorreia/work/hydra/benchmarks/data-forecast:/data-forecast",
        #"-v", "/home/claudiocorreia/work/hydra/benchmarks/azure-dataset:/azure-dataset",
        "-w", "/data-forecast/service",
        "timeseries-predictor-image",
        "python3", "predictor_bridge.py", work_dir, traces_dir, models_dir, str(idx)
    ]

    result = subprocess.run(docker_command, capture_output=True, text=True)

    end_time = time.time()
    print(f"LOG: predictor_bridge took {end_time - start_time:.4f} seconds, work size {len(work)}")
    
    output_filename = f'{work_dir}/output_{idx}.log'
    with open(output_filename, 'w') as output_file:
        output_file.write(result.stdout)

    leaderboard_filename = f'{work_dir}/leaderboard.pkl'
    with open(leaderboard_filename, "rb") as f:
        leaderboard = pickle.load(f)

    print("LOG: process " + str(idx) + " done")
    
    return leaderboard

def compute_leaderboard():
    global leaderboard_entries, trained_traces, trace_objects, trace_dir_drive
    print("** computing leaderboard **")

    # clean directory
    shutil.rmtree('running_traces/', ignore_errors=True)

    number_threads = 13 #13 for chronos

    print("spliting ", flush=True)
    online_trace_ids = list(trace_objects.keys())
    splited_work = [online_trace_ids[i::number_threads] for i in range(number_threads)]

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    leaderboard = {}

    print("ThreadPoolExecutor ", flush=True)

    with ThreadPoolExecutor(max_workers=number_threads + 1) as executor:

        futures = [executor.submit(run_predictor_process, chunk, idx, return_dict) for idx, chunk in enumerate(splited_work)]

        for future in futures:
            result = future.result()
            leaderboard.update(result)
        
        print(" ****** trying to shut down ************** ",  flush=True )



    leaderboard_entries = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
    
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
    #trained_traces = model_training.load_trained_traces()

    #leaderboard_thread = threading.Thread(target=leaderboard_routine)
    #leaderboard_thread.daemon = True  # Set the thread as a daemon so it will terminate when the main program ends
    #leaderboard_thread.start()

