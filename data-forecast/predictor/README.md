# Pipeline Forecasting

In this directory, there is a `default_config.json` file that contains many parameters that can be changed. The `raw_dataset` needs to point to a folder that stores the Azure 2019 Dataset, where the directory should have the following structure: "invocations_per_function_md.anon.d01.csv", "invocations_per_function_md.anon.d02.csv", up to 14 days.

## model_training.py

The `model_training.py` file is capable of training multiple models using AutoGluon and stores them locally. It uses all the traces in the `offline_trace_ids.txt` file. To call the code in `model_training.py`, you can use the `run-training.sh` script, which will call the `train_models_from_file()` function. This code uses the code inside `dataset_traces/` to load the traces.

### `train_models_from_file(config = {})`

If no arguments are passed to this function, it will load all the configurations from the local `default_config.json` file. This function will train all AutoGluon models for each trace in the `offline_trace_ids.txt`, and for each trace, it will store the trained models locally in the `AutogluonModels/Hydra_trace_id/` directory.
