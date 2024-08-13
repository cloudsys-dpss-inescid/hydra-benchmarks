import shared
import os
import sys
import concurrent.futures
import math
import matplotlib.pyplot as plt
import numpy as np

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../service')))
from service import cost_function

def get_cost_of_optimized_traces(optimized_traces_in_delta, simulation_dir, simulation_start, simulation_end, simulation_delta, model_type):
    # Count the number of computed leaderboards
    _, _, files = next(os.walk(simulation_dir))
    simulation_cost_for_optimzed_traces = 0
    optimized_traces = {}    
    current_timestamp = simulation_start
    file_name = f"leaderboard-{model_type}-{simulation_delta}-{simulation_start}.log"
    
    while( file_name in files ):

        top_leaderboard = shared.load_leaderboard(simulation_dir + file_name, optimized_traces_in_delta + len(optimized_traces))
        count_added = 0
        for trace_id in top_leaderboard.keys():
            if trace_id not in optimized_traces:
                optimized_traces[trace_id] = 0  # The value does not matter
                count_added += 1
                simulation_cost_for_optimzed_traces += cost_function.get_optimized_trace_cost(trace_id, simulation_start, current_timestamp + simulation_delta, simulation_end) 

            if count_added == optimized_traces_in_delta:
                break

        current_timestamp += simulation_delta
        file_name = f"leaderboard-{model_type}-{simulation_delta}-{current_timestamp}.log"

    return simulation_cost_for_optimzed_traces, optimized_traces

def get_cost_of_unoptimized_traces(all_traces, simulation_start, simulation_end):
    simulation_cost_for_unoptimized_traces = 0
    for trace_id in all_traces.keys():
        #print("-trace id " + trace_id)
        simulation_cost_for_unoptimized_traces += cost_function.get_normal_trace_cost(trace_id, simulation_start, simulation_end) 
    return simulation_cost_for_unoptimized_traces

def split_dict(d, n):
    keys = list(d.keys())
    chunk_size = math.ceil(len(keys) / n)
    return [dict((k, d[k]) for k in keys[i:i + chunk_size]) for i in range(0, len(keys), chunk_size)]

def get_simulation_cost(simulation_dir, simulation_start, simulation_end, simulation_delta, optimized_traces_in_delta, model_type):

    #first_leaderboard = simulation_dir + "leaderboard-" + str(simulation_start) + "-" + str(simulation_delta) + ".log"
    first_leaderboard = f"{simulation_dir}leaderboard-{model_type}-{simulation_delta}-{simulation_start}.log"
    all_traces = shared.load_leaderboard(first_leaderboard)

    optimized_cost, optimized_traces = get_cost_of_optimized_traces(optimized_traces_in_delta, simulation_dir, simulation_start, simulation_end, simulation_delta, model_type)

    # Remove the keys of optimized traces from all_traces
    for key in optimized_traces.keys():
        all_traces.pop(key, None)

    # Define the number of processes
    N = 40  

    # Split all_traces into N parts
    all_traces_parts = split_dict(all_traces, N)

    # Execute the function in parallel with multiple processes
    simulation_cost = optimized_cost
    with concurrent.futures.ProcessPoolExecutor(max_workers=N) as executor:
        future_to_part = {executor.submit(get_cost_of_unoptimized_traces, part, simulation_start, simulation_end): part for part in all_traces_parts}
        for future in concurrent.futures.as_completed(future_to_part):
            simulation_cost += future.result()

    return simulation_cost

def get_normal_cost(simulation_dir, simulation_start, simulation_end, simulation_delta, optimized_traces_in_delta, model_type):

    first_leaderboard = f"{simulation_dir}leaderboard-{model_type}-{simulation_delta}-{simulation_start}.log"
    all_traces = shared.load_leaderboard(first_leaderboard)

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

    return simulation_cost

def plot_simulation_cost(model_types, prediction_window):

    for type in model_types:

        model_cost = []
        for window_size in prediction_window:
            
            simulation_cost = get_simulation_cost(simulation_dir, simulation_start, simulation_end, window_size, optimized_traces_in_each_leaderboard, type)
            model_cost.append( simulation_cost )

        print(f"simulation_cost of {type} for windows {prediction_window} and picking top {optimized_traces_in_each_leaderboard} in the leaderboard: {model_cost}" )
        plt.plot(prediction_window, model_cost, label=type, marker=".")

def plot_normal_cost(model_types, prediction_window):

    simulation_cost = get_normal_cost(simulation_dir, simulation_start, simulation_end, prediction_window[0], optimized_traces_in_each_leaderboard, model_types[0])
    model_cost = [simulation_cost]*len(prediction_window)

    print(f"simulation_cost of normal cost for all windows: {model_cost}" )
    plt.plot(prediction_window, model_cost, label="normal cost", marker=".")

#simulation_dir = "../simulator/results/forcast-claudiocorreia-SvpXvpdT/"
simulation_dir = "results/comparation/"
simulation_start = 10080
simulation_end = 20159
#simulation_delta = 200
optimized_traces_in_each_leaderboard = 30
fig = plt.figure(figsize=(20, 10))

model_types = ["custom_autogluon", "average", "oracle"]
model_types = ["average"]
prediction_window = [100, 200, 400, 800]
plot_simulation_cost(model_types, prediction_window)


model_types = ["oracle"]
prediction_window = [200, 400, 800, 1440, 1600, 2880]
plot_simulation_cost(model_types, prediction_window)

model_types = ["randomly"]
prediction_window = [200, 400, 800]
plot_simulation_cost(model_types, prediction_window)

model_types = ["custom_autogluon"]
prediction_window = [100, 200, 400, 800, 1440, 1600, 2880, 4320]
plot_simulation_cost(model_types, prediction_window)
plot_normal_cost(model_types, prediction_window)


plt.xticks(prediction_window)
plt.legend()
plt.title("Cost simulation for 10k function with 4 leaderboard steps")
plt.xlabel("Window size used for prediction (minutes)")
plt.ylabel("Simuilation cost")
plt.savefig('models_comparation.png')

