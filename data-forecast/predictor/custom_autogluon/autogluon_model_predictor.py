#load all the required packages
import pandas as pd
import numpy as np
import time
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import stumpy
import sys
import os

# Add the path to the python modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import shared

#######################################################
################## Online processing ##################
#######################################################

##########
#Find Similar Function,  evaluate query trace from multiple starting points
##########

def get_similar_function(trace_obj, trained_traces):

  best_trace_id = []
  best_trace_euclidean_distance = float('inf')
  filtered_query_trace = trace_obj[1]

  ### Stumpy only works with 3 or more points, so I just copy the last value and append
  while len(filtered_query_trace) < 3:
    filtered_query_trace = np.append(filtered_query_trace, filtered_query_trace[-1])

  for obj_trace in trained_traces:
    
    filtered_trace_id = obj_trace[0]
    filtered_trace = obj_trace[1]
        
    distance_profile = stumpy.mass(filtered_query_trace, filtered_trace)

    min_timestamp_index = np.argmin(distance_profile)
    euclidean_distance = distance_profile[min_timestamp_index]

    if( euclidean_distance < best_trace_euclidean_distance ):
      best_trace_id = filtered_trace_id
      best_trace_euclidean_distance = euclidean_distance

  return best_trace_id

##########
# Recycle similar function past with new function trace, start_point_location is in minutes, the trace is also in minutes.
##########

recycle_time_window = 1440
def get_manufactured_function_past(query_obj, similar_trace_id, trained_objs, debug = False):

    query_trace_id = query_obj[0]
    usable_points = query_obj[1]

    similar_trace_obj = shared.find_in_nested_list(trained_objs, similar_trace_id)
    recycle_trace_id = similar_trace_obj[0]
    time_series = TimeSeriesDataFrame(similar_trace_obj[1])
    recycled_sample = time_series.slice_by_timestep(0, recycle_time_window * 2) # this is probably 2880 min, corresponding to 48h

    data = usable_points #default value in case the query is larger than 24h
    data["item_id"] = recycle_trace_id

    if len(usable_points["timestamp"]) < recycle_time_window:
        end_timestamp = pd.to_datetime( usable_points["timestamp"][ len(usable_points["timestamp"]) - 1 ] )
        timestamps = pd.date_range(end=end_timestamp, periods=recycle_time_window, freq='min')

        recycled_target_values = recycled_sample.loc[recycle_trace_id]["target"]
        recycled_array = np.array(recycled_target_values[:recycle_time_window])

        query_array = np.array(usable_points['target'])

        for i in range(1, len(usable_points)):
            recycled_array[-i] = query_array[-i]

        data = {
            'item_id': recycle_trace_id,
            'timestamp': timestamps,
            'target': recycled_array
        }

    df = pd.DataFrame(data)
    ts_df = TimeSeriesDataFrame(df)
    #I am using num_cpus=1 because it was causing problems when running in multiple processes
    manufactured_sample = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )
     
    manufactured_obj = [query_trace_id, manufactured_sample]

    return manufactured_obj    
  

def get_function_prediction(query_obj, similar_trace_id, models_location):

    query_trace = query_obj[1]

    #predictor_path = f"../predictor/autogluon_models/{similar_trace_id}"
    predictor_path = f"{models_location}/{similar_trace_id}"
    predictor = TimeSeriesPredictor.load(predictor_path)
    
    query_trace["item_id"] = similar_trace_id
    ts_df = TimeSeriesDataFrame(query_trace)
    resample_trace = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )

    predictions = predictor.predict(resample_trace, use_cache=False)

    return predictions.loc[similar_trace_id]["mean"]


def get_function_forecast(query_obj, trained_objs, models_location):

    start_time = time.time()
    query_obj_filtered = shared.get_filtered_dataset([query_obj])[0]
    trained_objs_filtered = shared.get_filtered_dataset(trained_objs)
    end_time = time.time()
    print(f"\nLOG: get_filtered_dataset took {end_time - start_time:.4f} seconds")

    start_time = time.time()
    similar_trace_id = get_similar_function(query_obj_filtered, trained_objs_filtered)
    end_time = time.time()
    print(f"LOG: get_similar_function took {end_time - start_time:.4f} seconds")

    start_time = time.time()
    manufactured_obj = get_manufactured_function_past(query_obj, similar_trace_id, trained_objs)  # replace points
    end_time = time.time()
    print(f"LOG: get_manufactured_function_past took {end_time - start_time:.4f} seconds")
    
    print( "predictor_trace_id: " + similar_trace_id)
    start_time = time.time()
    predictions = get_function_prediction(manufactured_obj, similar_trace_id, models_location)
    end_time = time.time()
    print(f"LOG: get_function_forecast took {end_time - start_time:.4f} seconds")

    print("first predicted value: " + str(np.array(predictions.values)[0]))

    return predictions


    
#######################################################
################## Offline processing #################
#######################################################


##################
# clustering function, To Be Implemented
##################

def get_cluster_dataset(traces_datapoints):
  return traces_datapoints



##################
# train AI, use autogluon to train over the multiple traces of the dataset and
# store the traces
#################

def train_predictor(trace_id):

    left_half_trace_points, _ = shared.get_splited_dataset([trace_id], shared.get_config_path("trace_dir_drive") )

    ts_df = TimeSeriesDataFrame(left_half_trace_points[0].raw_trace)
    single_trace = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )

    predictor_path = f"autogluon_models/{trace_id}"

    predictor = TimeSeriesPredictor(
        prediction_length=shared.get_config("autogluon_prediction_length"),
        path=predictor_path,
        target="target",
        cache_predictions=False,
        log_to_file=False,
        eval_metric=shared.get_config("autogluon_eval_metric")
    )

    predictor.fit(
        single_trace,
        #presets="chronos_tiny", it can also be "medium_quality"
        presets=shared.get_config("autogluon_presets"),
        time_limit=shared.get_config("autogluon_time_limit"),
        #excluded_model_types=["TemporalFusionTransformer"],
        #hyperparameters={
        #    "AutoARIMAModel": {},
        #},       
    )


def train_models(trace_ids_file_path):
    
    trace_ids = shared.load_dataset_ids(trace_ids_file_path) 
    
    for trace_id in trace_ids:
        train_predictor(trace_id)

#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):

    trace_ids = shared.load_dataset_ids(trace_ids_file_path) 
    left_half_trace_points = shared.get_trace_data(trace_ids)
    dataset = get_cluster_dataset(left_half_trace_points)

    return dataset


if __name__ == '__main__':

  train_models( shared.get_config_path("offline_traces_dir") )

