
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

def train_predictor(trace_id):

    left_half_trace_points, _ = shared.get_splited_dataset([trace_id], shared.get_config("trace_dir_drive") )

    ts_df = TimeSeriesDataFrame(left_half_trace_points[0].raw_trace)
    single_trace = ts_df.convert_frequency( shared.get_config("resample_interval") , agg_numeric= shared.get_config("aggregate_function"), num_cpus=1  )

    predictor_path = f"autogluon_models/{trace_id}"

    predictor = TimeSeriesPredictor(
        prediction_length=48,
        path=predictor_path,
        target="target",
        cache_predictions=False,
        log_to_file=False,
        eval_metric=shared.get_config("autogluon_eval_metric")
    )

    predictor.fit(
        single_trace,
        #presets="chronos_tiny", it can also be "medium_quality"
        presets=shared.get_config("autogluon_presets"),
        time_limit=shared.get_config("autogluon_time_limit"),
        #excluded_model_types=["TemporalFusionTransformer"],
        #hyperparameters={
        #    "AutoARIMAModel": {},
        #},       
    )


def train_models(trace_ids_file_path):
    
    trace_ids = shared.load_dataset_ids(trace_ids_file_path) 
    
    for trace_id in trace_ids:
        train_predictor(trace_id)

#####
# Main offline functions, to train a entire dataset of tarces
#####

def get_trained_dataset(trace_ids_file_path):

    trace_ids = shared.load_dataset_ids(trace_ids_file_path) 
    left_half_trace_points = shared.get_trace_data(trace_ids)
    dataset = get_cluster_dataset(left_half_trace_points)

    return dataset


if __name__ == '__main__':

  train_models( shared.get_config("offline_traces_dir") )






