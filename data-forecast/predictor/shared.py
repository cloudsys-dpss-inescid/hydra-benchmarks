
#load all the required packages
import pandas as pd
from dataclasses import dataclass, field
import numpy as np
import json
import os
from scipy.ndimage import gaussian_filter
import copy
import sys

#I use this to fild the relative path for the local files, I need this when a superior pyhton script calls this one
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data_manager')))
from data_manager import trace_generator


@dataclass
class Trace_Object:
    """Class to store traces of the dataset."""
    trace_id: str
    invocation_duration: int = 1
    memory_used_invocation: int = 1
    compilation_cost: int = 1
    raw_trace: pd.DataFrame = field(default_factory=pd.DataFrame)

simulation_configuration = {} #global variable holder

##################
# dataset loader, it loads from the local drive the traces for the provided functions IDs
##################

def get_splited_dataset(trace_ids, trace_dir_drive):

  ##### traces to use and comapre in search
  left_half_trace_points = []
  right_half_trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace(trace_id, simulation_configuration["raw_dataset"], trace_dir_drive)

    left_points = points[:len(points)//2]
    right_points = points[len(points)//2:]

    left_obj = Trace_Object(trace_id)
    left_obj.raw_trace = left_points
    right_obj = Trace_Object(trace_id)
    right_obj.raw_trace = right_points.reset_index()

    left_half_trace_points.append( left_obj )
    right_half_trace_points.append( right_obj )

  return left_half_trace_points, right_half_trace_points

def get_full_trace_data(trace_ids):

  ##### traces to use and comapre in search
  trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace(trace_id, get_config_path("raw_dataset"), get_config_path("trace_dir_drive"))
    points['timestamp'] = np.array(pd.to_datetime(points['timestamp']))
    
    trace_points.append( [trace_id, points] )

  return trace_points

def get_trace_data(trace_ids):

  ##### traces to use and comapre in search
  left_half_trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace(trace_id, get_config_path("raw_dataset"), get_config_path("trace_dir_drive"))

    left_points = points[:len(points)//2]
    left_half_trace_points.append( [trace_id, left_points] )

  return left_half_trace_points

def get_trace_data_fast(trace_ids, local_dataset):

  ##### traces to use and comapre in search
  left_half_trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace_fast(trace_id, get_config_path("raw_dataset"), get_config_path("trace_dir_drive"), local_dataset)

    left_points = points[:len(points)//2]
    left_half_trace_points.append( [trace_id, left_points] )

  return left_half_trace_points

##################
# resample trace, it receives a pandas datafrasme. The sum() should not be like this...
##################

def get_resample_trace(query_trace):


    trace_id = query_trace["item_id"][0]
    query_trace_resample = query_trace

    query_trace_resample['timestamp'] = pd.to_datetime(query_trace_resample['timestamp'])
    query_trace_resample.set_index('timestamp', inplace=True)
    query_trace_resample = query_trace_resample.resample(get_config("resample_interval"), origin='start').sum()
    query_trace_resample.reset_index(inplace=True)
    query_trace.reset_index(inplace=True) # the function was changing the input, meaning the query_trace was being mutated outside the function
    query_trace_resample["item_id"] = trace_id
    
    return query_trace_resample


##################
# filtering function, it filters the trace
##################

def get_filtered_dataset(raw_traces_datapoints):

    filtered_traces = []

    for obj_dataframe in raw_traces_datapoints:

        obj_dataframe = copy.deepcopy(obj_dataframe)
        trace_id = obj_dataframe[0]
        dataframe_cp = obj_dataframe[1]

        dataframe_cp['timestamp'] = pd.to_datetime(dataframe_cp['timestamp'])
        dataframe_cp = dataframe_cp['target'].astype(float)

        window_size = 5
        trace = dataframe_cp.rolling(window=window_size).max()

        for i in range(0, min(window_size, len(dataframe_cp))):
            trace[i] = dataframe_cp[i]

        trace = gaussian_filter(trace, sigma=2)

        filtered_traces.append([trace_id, trace])

    return filtered_traces

def load_dataset_ids(path):
    
    trace_ids = np.loadtxt( path, dtype=str).tolist()
    if isinstance(trace_ids, str): #in case there is a single trace id in the file
      trace_ids = [trace_ids]
    return trace_ids

def get_config(config):
  
  global simulation_configuration
  #if no configuration is provided, then load the default one
  if not simulation_configuration:
    with open( current_dir + "/default_config.json", 'r') as file:
        simulation_configuration = json.load(file)

  return simulation_configuration[config]

def get_config_path(config):
  
  config = get_config(config)

  return current_dir + "/" + config

def find_in_nested_list(nested_list, search_string):
    for index, sublist in enumerate(nested_list):
        if sublist[0] == search_string:
            return nested_list[index]
    return -1 

def generate_all_traces():
   
    trace_generator.generate_all_traces(get_config_path("raw_dataset"), get_config_path("trace_dir_drive"), get_config_path("trace_dir_drive") + "../all_traces_ids.csv" )
