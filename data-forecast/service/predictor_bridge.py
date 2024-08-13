import os
import sys
import pickle
import traceback
import cost_function
import requests
import json
import pandas as pd

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import predictor_factory

def get_trace(trace_id):
    url = "http://localhost:8055/get_trace"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"trace_id": trace_id})

    try:
        response = requests.get(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        response_data = response.json()

        # Convert each variable back to its appropriate type
        invocation_duration = int(response_data["invocation_duration"])
        memory_used_invocation = int(response_data["memory_used_invocation"])
        compilation_cost = int(response_data["compilation_cost"])
        raw_trace_json = response_data["dataframe"]
        
        # Convert the JSON back to a DataFrame
        raw_trace_df = pd.read_json(raw_trace_json, orient='records')

        return invocation_duration, memory_used_invocation, compilation_cost, raw_trace_df
    
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")


def compute_leaderboard(traces_dir, models_dir, trained_traces, predictor_mode, idx):

    return_dict = {}

    with open(f"{traces_dir}/work_{idx}", 'rb') as f:
        work = pickle.load(f)

    for trace_id in work:

        invocation_duration, memory_used_invocation, compilation_cost, raw_trace_df = get_trace(trace_id)
        current_obj = [trace_id, raw_trace_df]

        print("counter: " + str(len(return_dict)) +  " idx: " + str(idx) + " trace_id: " + trace_id )#+ " first value: " + str(single_trace.loc[trace_id, "target"].iat[1]))    
            
        if cost_function.is_trace_worthy_to_predict(trace_id, current_obj[1]["target"]):
            
            predictions = predictor_factory.get_function_forecast(current_obj, trained_traces, models_dir, predictor_mode)

            return_dict[trace_id] = cost_function.get_normal_cost(trace_id, predictions)
        else:
            return_dict[trace_id] = 0

    return return_dict

if __name__ == '__main__':

    try:
        work_dir = sys.argv[1]
        traces_dir = sys.argv[2]
        models_dir = sys.argv[3]
        predictor_mode = sys.argv[4]
        idx = sys.argv[5]
        
        trained_traces = predictor_factory.get_trained_dataset("../predictor/offline_trace_ids.txt", predictor_mode)

        leaderboard = compute_leaderboard(traces_dir, models_dir, trained_traces, predictor_mode, idx)


        output_filename = f'{work_dir}/leaderboard.pkl'
        with open(output_filename, 'wb') as f:
            pickle.dump(leaderboard, f)

        print(leaderboard)

    except Exception as e:
       # By this way we can know about the type of error occurring
        print("The error is: ",e)
        print(traceback.format_exc())