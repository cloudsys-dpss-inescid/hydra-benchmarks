# Forecasting Service

This directory contains the script `run_server_container.sh`, which launches a Docker container running an HTTP server capable of predicting trace forecasts for the Azure 2019 dataset. The server assumes the existence of previously trained models using AutoGluon. To train the models, navigate to the `/predictor` directory and run the `run-training.sh` script. This directory also contains a README.md with more information. The server provided here offers different HTTP endpoints, as detailed below. By default, this service is launched on port 8085.

Currently is only using the Chronos model, I have to change this: https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html

## Endpoints

### POST request: /add_invocation

This POST request requires three arguments as input:
1. **`timestamp`**: A string with the following representation: `"2019-01-07 03:30:00"`.
2. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.
3. **`invocation_count`**: A string containing an integer, representing how many times the trace/function was called at this timestamp.
4. **`invocation_duration`**: This is important to calculate the function cost to IoT, shuld the durantion and memory be diferent? after AoT.
5. **`memory_used_invocation`**: Bla Bla.
6. **`compilation_cost`**: Bla Bla.


Within the service, we assume a granularity of minutes. Depending on the timestamp, the service will either add the received `invocation_count` to the previous value for the same timestamp (within a minute's granularity) or create a new timestamp entry. When there is a gap between two timestamps larger than one minute, the service will fill these minutes with zeros, assuming the function was not called during this period.

Example usage:
```sh
curl -X POST http://localhost:8085/add_invocation -H "Content-Type: application/json" -d '{"timestamp":"2019-01-07 03:30:00", "trace_id":"trace123", "invocation_count":"30", "invocation_duration":"2", "memory_used_invocation":"300"}'
```

### POST request: /remove_trace_by_id

This POST request requires one argument as input:
1. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.

This will remove the function trace from the service and therefore it will no longer be evaluated in the leaderboard. This function should be called when the function code has been AoT compiled, as it no longer makes sense to predict it.

Example usage:
```sh
curl -X POST http://localhost:8085/remove_trace_by_id -H "Content-Type: application/json" -d '{"trace_id":"trace123"}'
```

### GET request: /leaderboard
This GET request returns a list of tuples, where each tuple contains a trace ID that has been uploaded through the `/add_invocation` endpoint, along with a corresponding cost value. The leaderboard only includes functions that have not yet been AOT-compiled. The cost is calculated based on multiple factors (feature to be implemented). The returned list is ordered from the highest costing function to the lowest costing function. This cost is based solely on a prediction of the future number of calls that a given trace may have. No input is required for this endpoint.

The leaderboard is automatically recomputed every 10 minutes, but this interval can be adjusted.

Example usage:
```sh
curl -X GET http://localhost:8085/leaderboard
```

### GET request: /compute_leaderboard
This GET request returns the same list as the `/leaderboard` endpoint but forces the service to recompute the list before responding to the request. This can be used to bypass the 10-minute interval, though it may result in slower response times.

Example usage:
```sh
curl -X GET http://localhost:8085/compute_leaderboard
```

## Simple Testing
This directory also contains the script `test_server.sh`, which can be used to test the prediction service. This script will upload 400 points for two distinct function traces. It requires access to the Azure original dataset and the correct path provided in the `raw_dataset_dir` variable within the script. It also assumes the existence of trained models in the local folder. After uploading the 400 points, the script will call the `/compute_leaderboard` endpoint and print the result.
