
#load all the required packages
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import shared


#######################################################
################## Offline processing #################
#######################################################


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

  for _, obj_trace in enumerate(dataset):

      time_series = TimeSeriesDataFrame(obj_trace.raw_trace)
      recycled_sample = time_series.slice_by_timestep(0, min_train_size * 2) # this is probably 2880 min, corresponding to 48h
      obj_trace.recycled_sample = recycled_sample

      # Resample train_sample to improve model training, 1h is usually fine
      train_sample_resampled = time_series.convert_frequency( shared.get_config("resample_interval") , agg_numeric=shared.get_config("aggregate_function") )

      predictor = TimeSeriesPredictor(
          prediction_length=shared.get_config("autogluon_prediction_length"),
          target="target",
          eval_metric=shared.get_config("autogluon_eval_metric"),
          cache_predictions=False,
          log_to_file=False,
          path=shared.current_dir + "/autogluon_models/Hydra_" + obj_trace.trace_id,
      )

      predictor.fit(
          train_sample_resampled,
          #presets="chronos_tiny", it can also be "medium_quality"
          presets=shared.get_config("autogluon_presets"),
          time_limit=shared.get_config("autogluon_time_limit"),
          hyperparameters={
              "NaiveModel": {},
          },          
      )

      obj_trace.predictor = predictor

  return dataset



#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(offline_trace_ids):

  left_half_trace_points, _ = shared.get_splited_dataset(offline_trace_ids, shared.get_config("trace_dir_drive") )
  filtered_traces = shared.get_filtered_dataset(left_half_trace_points)
  clustered_traces = get_cluster_dataset(filtered_traces)
  trained_traces = train_dataset(clustered_traces)

  return trained_traces


def train_models_from_file():

  offline_trace_ids = shared.load_dataset_ids( shared.get_config("offline_traces_dir") )
  
  return get_trained_dataset(offline_trace_ids)

#this function is used to load all the traces for the predictor, wihtout the trained models.
def load_trained_traces():
  
  offline_trace_ids = shared.load_dataset_ids( shared.get_config("offline_traces_dir") )

  left_half_trace_points, _ = shared.get_splited_dataset(offline_trace_ids, shared.get_config("trace_dir_drive") )
  filtered_traces = shared.get_filtered_dataset(left_half_trace_points)
  dataset = get_cluster_dataset(filtered_traces)

  for _, obj_trace in enumerate(dataset):

      time_series = TimeSeriesDataFrame(obj_trace.raw_trace)
      recycled_sample = time_series.slice_by_timestep(0, min_train_size * 2) # this is probably 2880 min, corresponding to 48h
      obj_trace.recycled_sample = recycled_sample

      obj_trace.predictor = TimeSeriesPredictor.load( shared.current_dir + "/autogluon_models/Hydra_" + obj_trace.trace_id)
  
  return dataset


if __name__ == '__main__':

  train_models_from_file()






