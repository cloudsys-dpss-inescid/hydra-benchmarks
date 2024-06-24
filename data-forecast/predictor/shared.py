
#load all the required packages
import pandas as pd
from dataclasses import dataclass, field
import numpy as np
from autogluon.timeseries import TimeSeriesPredictor
import json
from dataset_traces import trace_generator
import os
from scipy.ndimage import gaussian_filter


#I use this to fild the relative path for the local files, I need this when a superior pyhton script calls this one
current_dir = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Trace_Object:
    """Class to store traces of the dataset."""
    trace_id: str
    invocation_duration: int = 1
    memory_used_invocation: int = 1
    compilation_cost: int = 1
    raw_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    filtered_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    recycled_sample: pd.DataFrame = field(default_factory=pd.DataFrame) # this is suposed to be a TimeSeriesDataFrame, but I could not make ir work
    predictor: TimeSeriesPredictor = field(default_factory=TimeSeriesPredictor)

simulation_configuration = {} #global variable holder

##################
# dataset loader, it loads from the local drive the traces for the provided functions IDs
##################

def get_splited_dataset(trace_ids, trace_dir_drive):

  ##### traces to use and comapre in search
  left_half_trace_points = []
  right_half_trace_points = []
  for trace_id in trace_ids:

    points = trace_generator.read_csv_trace(trace_id, simulation_configuration["raw_dataset"], current_dir + "/" + trace_dir_drive)
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

    for i in range(0, min(window_size, len(raw_trace))):
      trace[i] = raw_trace[i]

    trace = gaussian_filter(trace, sigma=2)

    #raw_traces_datapoints[idx].insert(3,  "filtered", trace, True)
    obj_trace.filtered_trace = trace

  return raw_traces_datapoints

def load_dataset_ids(path):
    
    trace_ids = np.loadtxt( current_dir + "/" + path, dtype=str).tolist()
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