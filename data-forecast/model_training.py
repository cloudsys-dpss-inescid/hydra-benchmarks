
#load all the required packages
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from dataclasses import dataclass, field
from typing import List
import numpy as np
from scipy.stats import spearmanr
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import json
from dataset_traces import trace_generator



@dataclass
class Trace_Object:
    """Class to store traces of the dataset."""
    trace_id: str
    raw_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    filtered_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    recycled_sample: pd.DataFrame = field(default_factory=pd.DataFrame) # this is suposed to be a TimeSeriesDataFrame, but I could not make ir work
    predictor: TimeSeriesPredictor = field(default_factory=TimeSeriesPredictor)

simulation_configuration = {} #global variable holder

#######################################################
################## Offline processing #################
#######################################################

##################
# dataset loader, it loads from the local drive the traces for the provided functions IDs
##################

def get_splited_dataset(trace_ids, trace_dir_drive):

  ##### traces to use and comapre in search
  left_half_trace_points = []
  right_half_trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace(trace_id, simulation_configuration["raw_dataset"], trace_dir_drive)
    #points = pd.read_csv(trace_dir_drive + trace_id + '.csv')
    #points = TimeSeriesDataFrame.from_path(trace_dir_drive + trace_id + '.csv')

    left_points = points[:len(points)//2]
    right_points = points[len(points)//2:]

    left_obj = Trace_Object(trace_id)
    left_obj.raw_trace = left_points
    right_obj = Trace_Object(trace_id)
    right_obj.raw_trace = right_points.reset_index()

    left_half_trace_points.append( left_obj )
    right_half_trace_points.append( right_obj )

  return left_half_trace_points, right_half_trace_points

def load_dataset_ids(path):
    
    trace_ids = np.loadtxt(path, dtype=str).tolist()
    if isinstance(trace_ids, str): #in case there is a single trace id in the file
      trace_ids = [trace_ids]
    return trace_ids


##################
# filtering function, it filters the trace
##################

def get_filtered_dataset(raw_traces_datapoints):

  for idx, obj_trace in enumerate(raw_traces_datapoints):

    raw_trace = obj_trace.raw_trace
    raw_trace['timestamp'] = pd.to_datetime(raw_trace['timestamp'])
    raw_trace = raw_trace['target'].astype(float)

    window_size = 5
    trace = raw_trace.rolling(window=window_size).max()

    for i in range(0,window_size):
      trace[i] = raw_trace[i]

    trace = gaussian_filter(trace, sigma=2)

    #raw_traces_datapoints[idx].insert(3,  "filtered", trace, True)
    obj_trace.filtered_trace = trace

  return raw_traces_datapoints

##################
# clustering function, To Be Implemented
##################

def get_cluster_dataset(traces_datapoints):
  return traces_datapoints



##################
# train AI, use autogluon to train over the multiple traces of the dataset and
# store the traces
#################

min_train_size = 1440 # 24h has 1440 min
def train_dataset(dataset):

  for idx, obj_trace in enumerate(dataset):

      time_series = TimeSeriesDataFrame(obj_trace.raw_trace)
      recycled_sample = time_series.slice_by_timestep(0, min_train_size * 2) # this is probably 2880 min, corresponding to 48h
      obj_trace.recycled_sample = recycled_sample

      # Resample train_sample to improve model training, 1h is usually fine
      train_sample_resampled = time_series.convert_frequency(simulation_configuration["resample_interval"] , agg_numeric=simulation_configuration["aggregate_function"])

      predictor = TimeSeriesPredictor(
          prediction_length=simulation_configuration["autogluon_prediction_length"],
          target="target",
          eval_metric=simulation_configuration["autogluon_eval_metric"],
          cache_predictions=False,
          log_to_file=False,
          path="AutogluonModels/Hydra_" + obj_trace.trace_id,
      )

      predictor.fit(
          train_sample_resampled,
          presets=simulation_configuration["autogluon_presets"],
          time_limit=simulation_configuration["autogluon_time_limit"],
      )

      obj_trace.predictor = predictor

  return dataset

#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(offline_trace_ids, trace_dir_drive):

  left_half_trace_points, _ = get_splited_dataset(offline_trace_ids, simulation_configuration["trace_dir_drive"])
  filtered_traces = get_filtered_dataset(left_half_trace_points)
  clustered_traces = get_cluster_dataset(filtered_traces)
  trained_traces = train_dataset(clustered_traces)

  return trained_traces


def train_models_from_file(config = {}):
  global simulation_configuration

  #if no configuration is provided, then load the default one
  if not config:
    with open("default_config.json", 'r') as file:
        simulation_configuration = json.load(file)

  offline_trace_ids = load_dataset_ids(simulation_configuration["offline_traces_dir"])
  
  return get_trained_dataset(offline_trace_ids, simulation_configuration["trace_dir_drive"])



if __name__ == '__main__':

  train_models_from_file()






