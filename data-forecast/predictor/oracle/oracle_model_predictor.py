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
    query_tace = query_obj[1]

    # find the last timestamp
    ts_df = TimeSeriesDataFrame(query_tace)
    converted_ts_df = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )
    last_timestamp = converted_ts_df.index.get_level_values('timestamp').max()

    # get real trace
    df = shared.get_full_trace_data([trace_id])[0][1]
    ts_df = TimeSeriesDataFrame(df)
    converted_ts_df = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )
    
    #cut real trace
    real_prediction = converted_ts_df.query("timestamp > @last_timestamp")
    real_prediction = real_prediction.head( shared.get_config("autogluon_prediction_length"))
    real_prediction = real_prediction['target'].astype(float)

    return real_prediction

    
#######################################################
################## Offline processing #################
#######################################################


#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):

    return None

