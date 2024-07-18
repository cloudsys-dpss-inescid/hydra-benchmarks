import os
import sys
import pickle
import time
import copy
import traceback
import cost_function

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import shared, model_training, model_predictor


def compute_leaderboard(traces_dir, models_dir, trained_traces, idx):

    return_dict = {}

    for filename in os.listdir(traces_dir):
        file_path = os.path.join(traces_dir, filename)
        
        with open(file_path, 'rb') as f:
            current_obj = pickle.load(f)

        trace_id = current_obj[0]
        #trace = current_obj[1]

        print("counter: " + str(len(return_dict)) +  " idx: " + str(idx) + " trace_id: " + trace_id )#+ " first value: " + str(single_trace.loc[trace_id, "target"].iat[1]))    
            
        if cost_function.is_trace_worthy_to_predict(trace_id, current_obj[1]["target"]):
            
            predictions = model_predictor.get_function_forecast(current_obj, trained_traces, models_dir)

            return_dict[trace_id] = cost_function.get_normal_cost(trace_id, predictions)
        else:
            return_dict[trace_id] = 0

    
    return return_dict


if __name__ == '__main__':

    try:
        work_dir = sys.argv[1]
        traces_dir = sys.argv[2]
        models_dir = sys.argv[3]
        idx = sys.argv[4]
        
        trained_traces = model_training.get_trained_dataset("../predictor/offline_trace_ids.txt")

        leaderboard = compute_leaderboard(traces_dir, models_dir, trained_traces, idx)


        output_filename = f'{work_dir}/leaderboard.pkl'
        with open(output_filename, 'wb') as f:
            pickle.dump(leaderboard, f)

        print(leaderboard)

    except Exception as e:
       # By this way we can know about the type of error occurring
        print("The error is: ",e)
        print(traceback.format_exc())