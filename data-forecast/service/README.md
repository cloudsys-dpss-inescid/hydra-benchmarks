# HTTP Server Exposing the Service

This directory contains an HTTP server responsible for receiving notifications of function trace invocations and, when required, generating a leaderboard that identifies which functions will be more costly in the future. The server exposes endpoints that a FaaS platform can use to inform it about running functions and their invocation traces. All this information is stored in memory on the server. Upon request, the server will generate a leaderboard where it forecasts future invocations for each trace using a specified predictor, computes a cost for each trace, and sorts the leaderboard based on this cost. This leaderboard can later be used to decide which functions should be AoT (Ahead of Time compiled).

This server runs inside a Docker container and launches other containers to run multiple predictors in parallel. The server checks if the required ML models have been trained, and if not, it will trigger `run_training.sh` to train them. The script generates a local file called `server.log`, containing the server's runtime output. Initially, the idea was for the service to compute the leaderboard automatically every 5 minutes; however, that code is currently commented out, and it only computes the leaderboard when requested through the corresponding endpoint. By default, the service is launched on port 8085.

## Endpoints

All available endpoints are defined in the Python script `service/http_server.py`.

### POST request: `/add_invocation`

This POST request requires six arguments as input:
1. **`timestamp`**: A string with the format `"2019-01-07 03:30:00"`.
2. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.
3. **`invocation_count`**: An integer string representing how many times the trace/function was called at this timestamp.
4. **`invocation_duration`**: This is used to calculate the function's cost to AoT. It helps determine if the duration and memory usage differ after AoT.
5. **`memory_used_invocation`**: This is also important for calculating a more precise cost.
6. **`compilation_cost`**: Another factor that contributes to the final cost.

The service assumes a minute-level granularity. Depending on the timestamp, it will either add the `invocation_count` to the previous value for the same timestamp or create a new timestamp entry. If there is a gap larger than one minute between timestamps, the service will fill those minutes with zeros, assuming no invocations during that period.

Example usage:
```sh
curl -X POST http://localhost:8085/add_invocation -H "Content-Type: application/json" -d '{"timestamp":"2019-01-07 03:30:00", "trace_id":"trace123", "invocation_count":"30", "invocation_duration":"2", "memory_used_invocation":"300"}'
```

### POST request: /add_dataframe

This POST request requires five arguments as input:
1. **`dataframe`**: A Pandas dataframe transformed into JSON format.
2. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.
3. **`invocation_duration`**: This is important to calculate the function cost to AoT, shuld the durantion and memory be diferent? after AoT.
4. **`memory_used_invocation`**: This can also be important to calculate a more precise cost.
5. **`compilation_cost`**: This can also be important to calculate a more precise cost.

This endpoint functions similarly to `/add_invocation`, but accepts a dataframe, which is a more efficient way to upload multiple invocations. It is commonly used for simulation.


Example usage:
```sh
curl -X POST http://localhost:8085/add_invocation -H "Content-Type: application/json" -d '{"dataframe":"[{\"timestamp\":\"2019-01-07 23:58:00\", \"item_id\":\"trace123\", \"target\":\"30\"},{\"timestamp\":\"2019-01-07 23:59:00\", \"item_id\":\"trace123\", \"target\":\"288\"}, ... ]", "trace_id":"trace123", "invocation_duration":"2", "memory_used_invocation":"100", "compilation_cost":"100"}'
```

### POST request: /remove_trace_by_id

This POST request requires one argument as input:
1. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.

This will remove the function trace from the service and therefore it will no longer be evaluated in the leaderboard. This function should be called when the function code has been AoT compiled, as it no longer makes sense to predict it.

Example usage:
```sh
curl -X POST http://localhost:8085/remove_trace_by_id -H "Content-Type: application/json" -d '{"trace_id":"trace123"}'
```

### POST request: /set_predictor_mode

This POST request requires one argument as input:
1. **`predictor_mode`**: A string representing the predictor to use in the next leaderboard computation. Available options are: `custom_autogluon`, `average`, `oracle`, `randomly`, and `all_simultaneously`.

This sets the predictor to be used in the next leaderboard computation. It is particularly useful in simulations where you want to compute different leaderboards with different predictors. The default predictor is `custom_autogluon`. 

Example usage:
```sh
curl -X POST http://localhost:8085/remove_trace_by_id -H "Content-Type: application/json" -d '{"predictor_mode":"custom_autogluon"}'
```

### GET request: /leaderboard
This GET request returns a list of tuples, where each tuple contains a trace ID that has been uploaded through the `/add_invocation` endpoint, along with a corresponding cost value. The leaderboard only includes functions that have not yet been AOT-compiled. The cost is calculated based on multiple factors (feature to be implemented). The returned list is ordered from the highest costing function to the lowest costing function. This cost is based solely on a prediction of the future number of calls that a given trace may have. No input is required for this endpoint.

The leaderboard is automatically recomputed every 10 minutes, but this interval can be adjusted. (this feautre has been commented)

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

### GET request: /get_trace
This is an internal GET request used by the predictors to fetch trace data quickly. It takes one argument:
1. **`trace_id`**: A string representing the unique identifier of the function executed in Hydra/GraalVM, e.g., `"fac75689598f4a70c04eb92e12930a95f109d88ca612cae6afb5fea9969af425"`.

The response is a dictionary containing all information related to the trace, including `invocation_duration`, `memory_used_invocation`, `compilation_cost`, and a `dataframe`. The dataframe is the most important value, as it is used by the predictor to make a forecast.



## Cost Function

In this directory, you will find the script `cost_function.py`. It computes the cost for each trace forecast. There are two types of costs: one before AoT (normal cost) and one after AoT. These costs are used to sort the leaderboard. Currently, the cost is simply the sum of all invocations in the forecast, multiplied by 0.7 for the AoT cost. More variables should be considered, but this has not yet been implemented.
