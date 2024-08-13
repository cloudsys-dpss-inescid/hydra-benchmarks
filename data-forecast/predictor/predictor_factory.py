#load all the required packages
import matplotlib.pyplot as plt
import os
import sys

# Add the path to the python modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../custom_autogluon')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../oracle')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../average')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../randomly')))
from custom_autogluon import autogluon_model_predictor
from oracle import oracle_model_predictor
from average import average_model_predictor
from randomly import randomly_model_predictor

current_predictor=None

def get_predictor(model_name):
    global current_predictor

    if current_predictor != None:
        return current_predictor

    if model_name == "custom_autogluon":
        current_predictor = autogluon_model_predictor
    elif model_name == "oracle":
        current_predictor = oracle_model_predictor 
    elif model_name == "average":
        current_predictor = average_model_predictor
    elif model_name == "randomly":
        current_predictor = randomly_model_predictor                 
    else:
        current_predictor = autogluon_model_predictor

    return current_predictor

def get_trained_dataset(input, model_name):
    
    predictor = get_predictor(model_name)

    return predictor.get_trained_dataset(input)

def get_function_forecast(query_obj, trained_objs, models_location, model_name):
    
    predictor = get_predictor(model_name)
    
    return predictor.get_function_forecast(query_obj, trained_objs, models_location) 
          