#load all the required packages
import pandas as pd
import shared
from autogluon.timeseries import TimeSeriesDataFrame
import random




#######################################################
################## Online processing ##################
#######################################################

##########
#Find Similar Function,  evaluate query trace from multiple starting points
##########

def get_function_forecast(query_obj, trained_objs, models_location):

    query_trace = query_obj[1]

    # Find the last timestamp in the query trace
    query_trace_resample = shared.get_resample_trace(query_trace)
    last_timestamp = query_trace_resample["timestamp"].max()

    # Calculate the random value of the target values in the query trace, the value 134486 was picked from one of the most popular function on the dataset
    average_value = random.randint(0,134486) 

    # Number of future points to predict
    prediction_length = shared.get_config("autogluon_prediction_length")

    # Create a DataFrame with the predicted average values
    future_timestamps = pd.date_range(start=last_timestamp, periods=prediction_length + 1, freq=shared.get_config("resample_interval"))[1:]
    prediction = pd.DataFrame(data={'timestamp': future_timestamps, 'target': [average_value] * prediction_length})

    return prediction.set_index('timestamp')['target']


#######################################################
################## Offline processing #################
#######################################################


#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):

    return None

