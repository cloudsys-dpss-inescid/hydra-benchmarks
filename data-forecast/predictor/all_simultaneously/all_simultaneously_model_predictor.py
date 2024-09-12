#load all the required packages
import os
import sys
import numpy as np
from autogluon.timeseries import TimeSeriesDataFrame
import matplotlib.pyplot as plt
import shared
import pandas as pd

# Add the path to the python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../custom_autogluon')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../average')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../randomly')))
from custom_autogluon import autogluon_model_predictor
from oracle import oracle_model_predictor
from average import average_model_predictor
from randomly import randomly_model_predictor

#######################################################
################## Online processing ##################
#######################################################

##########
#Find Similar Function,  evaluate query trace from multiple starting points
##########

def get_function_forecast(query_obj, trained_objs, models_location):
    trace_id = query_obj[0]

    # stored data
    query_trace_raw = query_obj[1]
    query_trace_resample = shared.get_resample_trace(query_trace_raw)
    
    ## oracle model
    current_predictor = oracle_model_predictor 
    oracle_prediction = current_predictor.get_function_forecast(query_obj, trained_objs, models_location)

    ## real trace
    real_trace_raw = shared.get_full_trace_data([trace_id])[0][1]
    real_trace = shared.get_resample_trace(real_trace_raw)

    ## average prediction
    current_predictor = average_model_predictor 
    avg_data_points = current_predictor.get_function_forecast(query_obj, trained_objs, models_location)

    ## autogluon prediction
    current_predictor = autogluon_model_predictor
    autogluon_data_points, similar_trace_id = current_predictor.get_function_forecast(query_obj, trained_objs, models_location, debug = True)
    similar_trace = shared.get_full_trace_data([similar_trace_id])[0][1]
    _, manufactured_trace, recycle_points_original, print_recycle_window_for_match, print_cut_window, print_matched_subsequence = current_predictor.get_manufactured_function_past(query_obj, similar_trace_id, trained_objs, True)  # replace points
    manufactured_trace_resample = shared.get_resample_trace(manufactured_trace)

    ## random prediction
    current_predictor = randomly_model_predictor
    randomly_data_points = current_predictor.get_function_forecast(query_obj, trained_objs, models_location)


    fig = plt.figure(figsize =(20, 10)) 

    plt.subplot(6, 1, 1)
    plt.plot(real_trace["timestamp"], real_trace["target"], label="full real trace")
    plt.plot(query_trace_resample["timestamp"], query_trace_resample["target"], label="stored trace")
    plt.plot(oracle_prediction, label=f"oracle prediction fs:{sum(oracle_prediction)}")
    plt.plot(avg_data_points, label=f"average prediction ({np.round(avg_data_points[0])}) fs:{sum(avg_data_points)}")
    plt.plot(autogluon_data_points, label=f"autogluon prediction fs:{sum(autogluon_data_points)}")
    plt.title("Predictions, and frequency sum (fs)") 
    plt.legend()

    plt.subplot(6, 1, 2)
    plt.plot(randomly_data_points, label=f"randomly prediction fs:{sum(randomly_data_points)}")
    plt.title("Predictions, just the random one") 
    plt.legend()
    
    plt.subplot(6, 1, 3)
    plt.plot(similar_trace["timestamp"], similar_trace["target"], label="similar trace in cluster") 
    plt.plot(recycle_points_original["timestamp"], recycle_points_original["target"], label="points availabe to recycle")
    plt.plot(print_recycle_window_for_match["timestamp"], print_recycle_window_for_match["target"], "--", color="black", label="points used in Stumpy")
    plt.title("Similar function") 
    plt.legend()

    plt.subplot(6, 1, 4)
    plt.plot(similar_trace["timestamp"], similar_trace["target"], label="similar trace in cluster")
    plt.plot(print_cut_window["timestamp"], print_cut_window["target"], label="points recycled")
    plt.plot(print_matched_subsequence["timestamp"], print_matched_subsequence["target"], "--", color="black", label="subsequence matched by Stumpy")
    plt.title("Similar function and points recycled") 
    plt.legend()

    plt.subplot(6, 1, 5)
    plt.plot(real_trace_raw["timestamp"], real_trace_raw["target"], label="full real trace, raw")
    plt.plot(manufactured_trace["timestamp"], manufactured_trace["target"], label="trace used in autogluon, raw")
    plt.title("Recycled points") 
    plt.legend()

    plt.subplot(6, 1, 6)
    plt.plot(real_trace["timestamp"], real_trace["target"], label="full real trace, filtered")
    plt.plot(manufactured_trace_resample["timestamp"], manufactured_trace_resample["target"], label="trace used in autogluon, filtered") 
    plt.title("Recycled points, resample") 
    plt.legend()

    fig.tight_layout()

    plt.savefig(f"../predictor/debug/{query_trace_raw.shape[0]}w-predictions-{trace_id}.png")

    return oracle_prediction

    
#######################################################
################## Offline processing #################
#######################################################


#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):
    current_predictor = autogluon_model_predictor # I do this only for the autogluon model that requires

    return current_predictor.get_trained_dataset(trace_ids_file_path)

