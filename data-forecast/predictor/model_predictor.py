#load all the required packages
import pandas as pd
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import stumpy
import time
import shared
import os


#######################################################
################## Online processing ##################
#######################################################


##########
#Find Similar Function,  evaluate query trace from multiple starting points
##########

def get_similar_function(query_trace, traces_to_search):

  best_trace_idx = 0
  best_trace_euclidean_distance = float('inf')
  filtered_query_trace = query_trace.filtered_trace

  ### Stumpy only works with 3 or more points, so I just copy the last value and append
  while len(filtered_query_trace) < 3:
    filtered_query_trace = np.append(filtered_query_trace, filtered_query_trace[-1])

  for idx, obj_trace in enumerate(traces_to_search):
    filtered_trace = obj_trace.filtered_trace

    distance_profile = stumpy.mass(filtered_query_trace, filtered_trace)

    min_tyimestamp_index = np.argmin(distance_profile)
    euclidean_distance = distance_profile[min_tyimestamp_index]

    if( euclidean_distance < best_trace_euclidean_distance ):
      best_trace_idx = idx
      best_trace_euclidean_distance = euclidean_distance

  return traces_to_search[best_trace_idx]

##########
# Recycle similar function past with new function trace, start_point_location is in minutes, the trace is also in minutes.
##########

recycle_time_window = 1440
def get_manufactured_function_past(query_trace, similar_trace, debug = False):

  query_trace_id = query_trace.trace_id
  usable_points = query_trace.raw_trace

  recycle_trace_id = similar_trace.trace_id
  recycled_sample = similar_trace.recycled_sample

  data = usable_points #default value in case the query is larger than 24h
  data["item_id"] = recycle_trace_id
  
  if  len(usable_points["timestamp"]) < recycle_time_window:
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
  query_trace.recycled_sample = manufactured_sample

  #### Print for debug
  # Plot manufactured function
  if debug:
    plt.figure(figsize=(20, 6))

    plt.plot(similar_trace.recycled_sample.loc[recycle_trace_id]["target"], color="blue", label="similar_trace.recycled_sample")
    plt.plot(ts_df.loc[recycle_trace_id], color="black", label="final recycled_sample")
    plt.plot(query_trace.raw_trace["timestamp"], query_trace.raw_trace["target"] , color="orange", label="query_trace")
    plt.legend()

    plt.title("Trace id: " + query_trace_id )
    plt.legend()

  return query_trace

##########
# Use autogluon to forecast function future
##########

def get_function_forecast(trace_id, trace, predictor, debug = False, output_dir = ""):

  predictions = predictor.predict(trace, model=predictor.model_best)

  #### Print for debug
  # Plot manufactured function
  if debug:

    # Get the names of all trained models
    model_names = predictor.model_names()
    train_summary = predictor.fit_summary(verbosity = 0)

    number_of_plots = len(model_names)

    plt.figure(figsize=(20, 20))
    plt.subplot(number_of_plots, 1, 1)

    counter = 1
    # Loop through each model to predict and plot
    for model_name in model_names:

        start_time = time.time()
        predictions = predictor.predict(trace, model=model_name)
        end_time = time.time()

        y_pred = predictions.loc[trace_id]

        plt.subplot(number_of_plots, 1, counter)
        plt.plot(trace.loc[trace_id]["target"], color="blue")
        plt.plot(y_pred["mean"], color="orange", label="Predicted time series values")

        plt.title('AutoGluon forecasts **' + model_name + '** -- train: ' + str( round(train_summary["model_fit_times"][model_name], 4) ) + "s train prediction: "  + str( round(train_summary["model_pred_times"][model_name],4) ) + "s test prediction: "  + str( round( end_time - start_time,4) ) + "s"    )
        plt.legend()

        plt.subplots_adjust(hspace=1)
        plt.fill_between(y_pred.index, y_pred["0.1"], y_pred["0.9"], color="red", alpha=0.1, label="10%-90% confidence interval")
        plt.legend()
        counter += 1

    # Save the figure for each model
    plt.savefig(output_dir + "get_function_forecast_" + trace_id, bbox_inches='tight')
    #plt.show()  # Close the figure to avoid displaying it in the notebook

  return predictions.loc[trace_id]["mean"]



##########
# Decide if the given trace should be evaluated to be AOT
##########

def is_trace_worthy_of_forecast(query_trace, cut_index_size):

  if len(query_trace.raw_trace) < cut_index_size:
    return False

  if sum(query_trace.raw_trace["target"]) <= 0:
    return False

  # TODO
  # if apenas teve uma chavamada return false


  return True

#####
# Load running fucntion trace, it loads all the points from the start until the current timestamp
#####

def get_query_trace(trace_id, cut_index_size, step_index, trace_dir_drive):

  _, right_half_trace_points = shared.get_splited_dataset([trace_id], trace_dir_drive)
  query_trace = right_half_trace_points[0]

  # cut the points
  to_recycle_sample = TimeSeriesDataFrame(query_trace.raw_trace)

  first_non_zero_index = int(np.argmax(query_trace.raw_trace["target"] > 0))

  if first_non_zero_index < step_index:

    query_trace.raw_trace = query_trace.raw_trace[first_non_zero_index: step_index]
    query_trace.raw_trace = query_trace.raw_trace.reset_index()

    query_trace.recycled_sample = to_recycle_sample.slice_by_timestep(first_non_zero_index, step_index )

    #### here I decide if the function is ready to be evaluated or
    if is_trace_worthy_of_forecast(query_trace, cut_index_size):
      return query_trace

  return None

#####
# Compute the cost of a function on the datacenter base on prediciton
#####

def get_aot_cost(trace_id, data_points):
  
  forecast_cost =  sum(data_points)
  compilation_cost = 1000
  reduction_factor = 0.7 #this needs to be configure based on real data

  return forecast_cost*reduction_factor + compilation_cost


def get_normal_cost(trace_id, data_points):
  
  forecast_cost =  sum(data_points)

  return forecast_cost

def is_trace_worthy_of_AoT(trace_id, prediction):

  aot_cost = get_aot_cost(trace_id, prediction)
  normal_cost = get_normal_cost(trace_id, prediction)

  if normal_cost > aot_cost:
    return True

  return False


#####
# Main online code, given a trace it forecasts it future calls
#####

def get_trace_forecast(trace_id, query_trace, trained_traces, trace_dir_drive, debug = False, log = False, output_dir = ""):

  start_time = time.time()
  query_trace = shared.get_filtered_dataset([query_trace])[0]
  end_time = time.time()
  print(f"\nLOG: get_filtered_dataset took {end_time - start_time:.4f} seconds")

  start_time = time.time()
  similar_trace = get_similar_function(query_trace, trained_traces)
  end_time = time.time()
  print(f"LOG: get_similar_function took {end_time - start_time:.4f} seconds")


  start_time = time.time()
  query_trace = get_manufactured_function_past(query_trace, similar_trace, debug)  # replace points
  end_time = time.time()
  print(f"LOG: get_manufactured_function_past took {end_time - start_time:.4f} seconds")
  prediction = ""

  start_time = time.time()
  prediction = get_function_forecast(similar_trace.trace_id, query_trace.recycled_sample, similar_trace.predictor, debug = debug, output_dir = output_dir)
  end_time = time.time()
  print(f"LOG: get_function_forecast took {end_time - start_time:.4f} seconds, query trace id {query_trace.trace_id}, in processed by pid: {os.getpid()} ",  flush=True )

  #print(f"get_function_forecast took {end_time - start_time:.4f} seconds, similar id {similar_trace.trace_id}, query trace id {query_trace.trace_id} query trace:" )
  #print(query_trace.recycled_sample)

  if log:
    fig  = plt.figure(figsize=(20, 6))


    plt.subplot(3, 1, 1)
    #print(similar_trace.raw_trace.loc["ada2b904c7122b0eb80175e637b7501bfea46fe59cf37c34a144e25078c1abc2"])
    plt.plot(similar_trace.raw_trace["timestamp"], similar_trace.raw_trace["target"], color="blue", label="similar trace")
    plt.plot(similar_trace.raw_trace["timestamp"], similar_trace.filtered_trace, color="orange", label="similar trace (filtered)")

    _ , right_half_trace_points_similar = shared.get_splited_dataset([similar_trace.trace_id], trace_dir_drive)
    right_half_trace_points_similar[0].raw_trace['timestamp'] = pd.to_datetime(right_half_trace_points_similar[0].raw_trace['timestamp'])
    plt.plot(right_half_trace_points_similar[0].raw_trace["timestamp"], right_half_trace_points_similar[0].raw_trace["target"], color="grey", label="removed part")

    similar_resampled = similar_trace.recycled_sample.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1 )
    plt.plot(similar_resampled.loc[similar_trace.trace_id], color="coral", label="similar trace (time resampling)")

    if  len(query_trace.raw_trace["timestamp"]) < recycle_time_window:
      recycled_used_size = len(query_trace.recycled_sample.loc[similar_trace.trace_id]["target"])
      for i in range(0, recycled_used_size):
        similar_resampled.loc[similar_trace.trace_id, "target"].iat[i] = query_trace.recycled_sample.loc[similar_trace.trace_id, "target"].iat[i]

      used_values_manufactured = similar_resampled.slice_by_timestep(0, recycled_used_size )
      plt.plot(used_values_manufactured.loc[similar_trace.trace_id], color="black", label="final recycled_sample", linestyle='dashed')


    plt.title('Similar trace found in dataset')
    plt.legend()

    plt.subplot(3, 1, 2)
    left_half_trace_points, right_half_trace_points = shared.get_splited_dataset([trace_id], trace_dir_drive)
    right_half_trace_points[0].raw_trace['timestamp'] = pd.to_datetime(right_half_trace_points[0].raw_trace['timestamp'])
    left_half_trace_points[0].raw_trace['timestamp'] = pd.to_datetime(left_half_trace_points[0].raw_trace['timestamp'])
    plt.plot(right_half_trace_points[0].raw_trace["timestamp"], right_half_trace_points[0].raw_trace["target"], color="skyblue", label="original/raw query trace")
    plt.plot(left_half_trace_points[0].raw_trace["timestamp"], left_half_trace_points[0].raw_trace["target"], color="grey", label="removed part")
    plt.plot(query_trace.raw_trace["timestamp"], query_trace.raw_trace["target"] , color="orange", label="query_trace, " + str(len(query_trace.raw_trace["target"])) + " points")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(query_trace.recycled_sample.loc[similar_trace.trace_id]["target"], color="black", label="final recycled_sample",  zorder=10)
    plt.plot(prediction, color="orange", label= similar_trace.predictor.model_best +  " forecast, " + str(len(prediction)) + " points",  zorder=10)
    XaxisLimits = plt.xlim()
    plt.plot(right_half_trace_points[0].raw_trace["timestamp"], right_half_trace_points[0].raw_trace["target"], color="skyblue",  zorder=1)
    plt.xlim(XaxisLimits)

    plt.legend()
    plt.savefig(output_dir + trace_id + ".png", bbox_inches='tight')
    plt.close()



  return prediction


