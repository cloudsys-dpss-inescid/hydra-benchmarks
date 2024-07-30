I need to improve this!

# Pipeline Trace Data

This directory contains data traces in a special format to be used in the pipeline. Each time the pipeline needs a trace, it will try to fetch the trace from the directory `/traces_datapoints/`. If the trace is not yet in the directory, it can use the function `generate_and_plot_trace_id()` inside `trace_generator.py`. This function will generate the required trace and a plot of the trace stored in `/traces_plots/`. The plots are only for debugging purposes and are not required otherwise.

## Directory Structure

I assume there is a directory with the original traces that contains a file for each day of the Azure dataset with the following names: "invocations_per_function_md.anon.d01.csv", "invocations_per_function_md.anon.d02.csv", up to 14 days.

## Available Functions

### `generate_and_plot_trace_id(trace_id, dataset_dir, result_dir)`

This function takes 3 arguments and generates the traces in `/traces_datapoints/`. The arguments are as follows:

1. `trace_id`: a string of the trace ID.
2. `dataset_dir`: a string of the path to the directory containing all the original traces for each day.
3. `result_dir`: the directory where there should be 2 folders, `traces_datapoints` and `traces_plots`. This folder can be the current folder where this README is located.

### `generate_trace_ids_file(dataset_dir, all_traces_ids_file)`

This function reads all the existing traces in the original dataset and creates a file containing only these IDs, one ID per line. This is useful for picking some function IDs when needed.

### `generate_all_traces(dataset_dir, result_dir, all_traces_ids_file)`

This function reads the previous file, containing all the trace IDs, and runs the `generate_and_plot_trace_id()` function for each trace. This function takes a long time to run because there are thousands of traces. It carefully generates the traces only if they are not already in the `/traces_datapoints/` directory to avoid repeated work. This function is useful for seeing many function traces, their plots, and IDs, and picking some for testing.

## Additional Tools

This directory also provides a `trace_generator.ipynb` file that can be used in Google Colab to run the previous functions in a more interactive and easily debuggable environment.
