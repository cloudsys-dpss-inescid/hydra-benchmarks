import shared
import os
import sys
import concurrent.futures
import math

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../service')))
from service import cost_function

def get_cost_of_optimized_traces(optimized_traces_in_delta, simulation_dir, simulation_start, simulation_end, simulation_delta):
    # Count the number of computed leaderboards
    _, _, files = next(os.walk(simulation_dir))
    file_count = len(files)

    simulation_cost_for_optimzed_traces = 0
    optimized_traces = {}
    last_leaderboard_timestamp = simulation_start + simulation_delta * file_count
    for current_timestamp in range(simulation_start, last_leaderboard_timestamp, simulation_delta):
        file_leaderboard = simulation_dir + "leaderboard-" + str(current_timestamp) + "-" + str(simulation_delta) + ".log"
        top_leaderboard = shared.load_leaderboard(file_leaderboard, optimized_traces_in_delta + len(optimized_traces))
        
        count_added = 0
        for trace_id in top_leaderboard.keys():
            if trace_id not in optimized_traces:
                optimized_traces[trace_id] = 0  # The value does not matter
                count_added += 1
                simulation_cost_for_optimzed_traces += cost_function.get_optimized_trace_cost(trace_id, simulation_start, current_timestamp + simulation_delta, simulation_end) 
            
            if count_added == optimized_traces_in_delta:
                break

    return simulation_cost_for_optimzed_traces, optimized_traces

def get_cost_of_unoptimized_traces(all_traces, simulation_start, simulation_end):
    simulation_cost_for_unoptimized_traces = 0
    for trace_id in all_traces.keys():
        print("-trace id " + trace_id)
        simulation_cost_for_unoptimized_traces += cost_function.get_normal_trace_cost(trace_id, simulation_start, simulation_end) 
    return simulation_cost_for_unoptimized_traces

def split_dict(d, n):
    keys = list(d.keys())
    chunk_size = math.ceil(len(keys) / n)
    return [dict((k, d[k]) for k in keys[i:i + chunk_size]) for i in range(0, len(keys), chunk_size)]

simulation_dir = "../simulator/results/forcast-claudiocorreia-FmC2v6pb/"
simulation_start = 5760
simulation_end = 20159
simulation_delta = 200
optimized_traces_in_delta = 30

first_leaderboard = simulation_dir + "leaderboard-" + str(simulation_start) + "-" + str(simulation_delta) + ".log"
all_traces = shared.load_leaderboard(first_leaderboard)

optimized_cost, optimized_traces = get_cost_of_optimized_traces(optimized_traces_in_delta, simulation_dir, simulation_start, simulation_end, simulation_delta)

# Remove the keys of optimized traces from all_traces
for key in optimized_traces.keys():
    all_traces.pop(key, None)

# Define the number of processes
N = 40  

# Split all_traces into N parts
all_traces_parts = split_dict(all_traces, N)

# Execute the function in parallel with multiple processes
simulation_cost = 0
with concurrent.futures.ProcessPoolExecutor(max_workers=N) as executor:
    future_to_part = {executor.submit(get_cost_of_unoptimized_traces, part, simulation_start, simulation_end): part for part in all_traces_parts}
    for future in concurrent.futures.as_completed(future_to_part):
        simulation_cost += future.result()

print("simulation_cost: " + str(simulation_cost))
