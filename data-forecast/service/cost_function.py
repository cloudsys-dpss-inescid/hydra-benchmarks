from autogluon.timeseries import TimeSeriesPredictor

#####
# Compute the cost of a function on the datacenter base on prediciton
#####

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