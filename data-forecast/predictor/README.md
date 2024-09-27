# Predictors

This folder contains multiple predictors that are used by the forecasting service to generate the leaderboards. The goal of each predictor is to forecast how many times a given function may be invoked in the future. Each predictor receives as input the past trace observed by the service for a particular function. Note that this trace may be short if the function is new. Based on this limited information, each predictor attempts to forecast the function’s invocations in different ways.

The interaction between the service and each predictor is handled through the `predictor_factory.py` script. This Python script abstracts the service from the details of each predictor, so the service only needs to provide a string specifying which predictor to use. Most predictors are fairly simple, except for the `custom_autogluon` predictor, which uses Machine Learning (ML) models and requires prior training (this is done automatically).

The directory contains various files and a separate folder for each predictor. Below, we provide a description of each predictor, followed by more details about the other files.

## Predictors Description

All predictors implement the same interface, with two functions: `get_trained_dataset()` and `get_function_forecast()`. To add a new predictor, simply create a new directory for the predictor and modify the `predictor_factory.py` script. Each predictor receives a function trace, which may be short, as input in the `get_function_forecast()` function, and returns a DataFrame that forecasts the future invocations of the function. This returned object has two columns: a timestamp column with minute-level granularity and a target column with the number of invocations for each given minute. Currently, the forecast is for 48 minutes into the future, but this can be adjusted in the `default_config.json` file. The prediction approach for each predictor is as follows:

- [custom_autogluon](custom_autogluon): This is the most complex predictor and the only one based on ML. It uses the [AutoGluon](https://auto.gluon.ai/stable/index.html) framework to manage ML models. Unlike other predictors, this one requires model training before use. Training is performed automatically when the service is executed. If the folder `predictor/custom_autogluon/autogluon_models/` is empty, the service trains a model for each function listed in `predictor/offline_trace_ids.txt` and stores the trained models in this folder. The `default_config.json` file allows various configurations, and we are currently using the `chronos_tiny` model, which requires a GPU. You can try [other models](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html), but note that some may require modifications to the `predictor.fit` function in `autogluon_model_predictor.py`. In this script, the `get_function_forecast()` function is where the magic happens. First, we apply a Gaussian filter to the input trace and all the traces used for training, then we find which trained traces best match the input trace. Since the input trace is short, we look for similar functions with a longer past trace. This comparison is done using the [Stumpy](https://stumpy.readthedocs.io/en/latest/) framework. Once a similar function is found, we extend the input trace with the similar function’s past history, which allows us to feed more data to AutoGluon, improving the predictions. Note that our prediction depends heavily on finding a good similar function, which is crucial. In the future, we plan to implement an intelligent trace clustering system. For now, the traces are manually selected in the `offline_trace_ids.txt` file.

- [average](average): This predictor calculates the average invocation of the input trace and generates a forecast based solely on this average. It does not attempt to capture any sinusoidal behavior present in the input trace.

- [randomly](randomly): This predictor selects a random value (within the interval 0 to 134486) and generates a forecast consisting of this random value across future timestamps. It’s essentially a random guess for the number of future invocations.

- [oracle](oracle): This is the perfect predictor. It returns the actual future invocations of the requested function by finding the function ID in the Azure dataset and retrieving the trace that represents its future invocations.

- [all_simultaneously](all_simultaneously): This predictor is used solely for debugging purposes. It runs all the other predictors and plots their outputs against the actual data. The resulting figures, one for each trace prediction, are saved in the `predictor/debug/` directory. This predictor is slow due to the figure generation, so use it with caution when running the service on many traces.

## Other Files

There are other important files in this directory, described below:

- [default_config.json](default_config.json): This file contains many parameters essential for running the predictors, particularly `custom_autogluon`. Be careful when changing these values, as, for example, reducing the `resample_interval` can make predictions slower and less accurate. The ML models do not perform well with small timestamp granularity.

- [offline_trace_ids.txt](offline_trace_ids.txt): This file lists all the functions considered potential similar functions, each of which will have a trained model stored in `predictor/custom_autogluon/autogluon_models/`. The models are trained by running the script `predictor/custom_autogluon/autogluon_models/run-training.sh`. In the future, each of these functions should represent a cluster of dataset traces, but unfortunately, this clustering has not yet been implemented.

- [shared.py](shared.py): This Python script contains a class used to store traces and metadata (e.g., ID, memory usage, etc.). It also provides functions that are utilized by various components of the service.

