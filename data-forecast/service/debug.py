import subprocess
import os
import sys
import pickle
import shutil
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import shared
import time

online_trace_ids = shared.load_dataset_ids("../service/debug/online_trace_ids.txt") 
traces_to_predic = []

print("loading online ", flush=True)
online_trace_ids = online_trace_ids[:10000]
#traces_to_predic = shared.get_trace_data(online_trace_ids)
print("loading online done ", flush=True)


def run_predictor_process(work, idx, return_dict):

    print(f"Hi from process idx {idx}", flush=True)

    work_dir = f"running_traces/process_{idx}"
    traces_dir = f"{work_dir}/traces"
    models_dir = f"{work_dir}/autogluon_models"
    os.makedirs(traces_dir, exist_ok=True)
    shutil.copytree('../predictor/autogluon_models', models_dir, dirs_exist_ok=True)
    
    
    start_time = time.time()
    for trace_id in work:
        item_to_predic = shared.get_trace_data([trace_id])[0]
        file_name = os.path.join(traces_dir, f"{trace_id}.pkl")
        
        with open(file_name, 'wb') as f:
            pickle.dump(item_to_predic, f)

    end_time = time.time()
    print(f"LOG: loading traces took {end_time - start_time:.4f} seconds")
    

    start_time = time.time()
    result = subprocess.run(["python3", "predictor_bridge.py", work_dir, traces_dir, models_dir, str(idx)], capture_output=True, text=True)
    end_time = time.time()
    print(f"LOG: predictor_bridge took {end_time - start_time:.4f} seconds")
    

    #print("aqui " + result.stdout )
    
    output_filename = f'{work_dir}/output_{idx}.log'
    with open(output_filename, 'w') as output_file:
        output_file.write(result.stdout)

    leaderboard_filename = f'{work_dir}/leaderboard.pkl'
    with open(leaderboard_filename, "rb") as f:
        leaderboard = pickle.load(f)

    print("LOG: process " + str(idx) + " done")
    
    return leaderboard



    
# clean directory
#shutil.rmtree("running_traces/")
shutil.rmtree('running_traces/', ignore_errors=True)


number_threads = 13
print("spliting ", flush=True)
splited_work = [online_trace_ids[i::number_threads] for i in range(number_threads)]



manager = multiprocessing.Manager()
return_dict = manager.dict()

print("ThreadPoolExecutor ", flush=True)

with ThreadPoolExecutor(max_workers=number_threads + 1) as executor:
    futures = [executor.submit(run_predictor_process, chunk, idx, return_dict) for idx, chunk in enumerate(splited_work)]

    leaderboard = {}
    for future in futures:
        result = future.result()
        leaderboard.update(result)
    
    print(" ****** trying to shut down ************** ",  flush=True )



leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))

print(leaderboard)
    #executor.shutdown(wait=False)


















