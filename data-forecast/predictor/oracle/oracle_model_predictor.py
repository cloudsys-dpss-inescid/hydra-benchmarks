#load all the required packages
import pandas as pd
import numpy as np
import time
import shared
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import stumpy
import matplotlib.pyplot as plt



#######################################################
################## Online processing ##################
#######################################################

##########
#Find Similar Function,  evaluate query trace from multiple starting points
##########

def get_function_forecast(query_obj, trained_objs, models_location):

    trace_id = query_obj[0]
    query_trace = query_obj[1]

    # find the last timestamp
    query_trace_resample = shared.get_resample_trace(query_trace)
    last_timestamp = query_trace_resample["timestamp"].max()

    # get real trace
    real_trace = shared.get_full_trace_data([trace_id])[0][1]
    real_trace_resample = shared.get_resample_trace(real_trace)

    print("get_function_forecast")
    #cut real trace
    real_prediction = real_trace_resample.query("timestamp > @last_timestamp")
    real_prediction = real_prediction.head( shared.get_config("autogluon_prediction_length"))
    real_prediction['target'] = real_prediction['target'].astype(float)

    return real_prediction.set_index('timestamp')['target']

    
#######################################################
################## Offline processing #################
#######################################################


#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):

    return None

