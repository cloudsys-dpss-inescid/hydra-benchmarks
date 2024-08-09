import sys
import os

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../predictor')))
from predictor import shared

#####
# Compute the cost of a function on the datacenter base on prediciton
#####
def get_normal_trace_cost(trace_id, simulation_start, simulation_end):

  full_trace = shared.get_full_trace_data([trace_id])[0][1]
  full_trace = full_trace['target'].astype(float)

  not_optimized_trace = full_trace[simulation_start:simulation_end]

  cost = get_normal_cost(trace_id, not_optimized_trace) 

  return cost

def get_optimized_trace_cost(trace_id, simulation_start, optimized_timestamp, simulation_end):

  full_trace = shared.get_full_trace_data([trace_id])[0][1]
  full_trace = full_trace['target'].astype(float)

  not_optimized_trace = full_trace[simulation_start:optimized_timestamp]
  optimized_trace = full_trace[optimized_timestamp:simulation_end]

  cost = get_normal_cost(trace_id, not_optimized_trace) + get_aot_cost(trace_id, optimized_trace)

  return cost

def get_aot_cost(trace_id, data_points):
  
  forecast_cost =  sum(data_points)
  compilation_cost = 1000
  reduction_factor = 0.7 #this needs to be configure based on real data

  return round(forecast_cost*reduction_factor + compilation_cost)


def get_normal_cost(trace_id, data_points):
  
  forecast_cost =  sum(data_points)

  return  round(forecast_cost)

def is_trace_worthy_to_predict(trace_id, data_points):

  current_cost =  sum( data_points )

  if current_cost > 200:
    return True

  return False

def is_trace_worthy_of_AoT(trace_id, prediction):

  aot_cost = get_aot_cost(trace_id, prediction)
  normal_cost = get_normal_cost(trace_id, prediction)

  if normal_cost > aot_cost:
    return True

  return False