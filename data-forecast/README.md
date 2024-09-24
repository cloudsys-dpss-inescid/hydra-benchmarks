# Forecasting Service

This repository contains a service provided by an HTTP server that predicts which FaaS functions will be more costly in the near future.

## Introduction
This repository contains a service designed for a FaaS platform that can decide which functions will be more invoked in the future. This work aims to complement previous work in [CloudJIT](https://dl.acm.org/doi/10.1145/3617651.3622990), which tries to perform AoT compilation in some functions to improve efficiency. However, currently, CloudJIT chooses these functions based on a fixed threshold, and we wanted to predict these functions' behavior in the future to make a more informed decision on which function should be AoT. Previous work has used ARIMA models to forecast future function invocations in the context of FaaS, such as [IceBreaker](https://dl.acm.org/doi/10.1145/3503222.3507750) and [Serverless in the Wild](https://www.usenix.org/conference/atc20/presentation/shahrad). We have followed the same path. In this repository, we implement different forecast predictors, where the most complex is based on the [AutoGluon](https://auto.gluon.ai/stable/index.html) framework, which offers many machine learning time series predictors in a black-box view, including the ARIMA model. Additionally, we have implemented an HTTP server that runs as a live service, receiving notifications of function invocations and generating leaderboards based on which function will be more costly for the FaaS platform in the future. This leaderboard could then be used by any FaaS platform to choose which functions should be AoT first.

In addition to our service, which can be launched in a container running in the background, we also provide a simulator that takes the [Azure 2019 dataset](https://www.usenix.org/conference/atc20/presentation/shahrad) and uses it to feed into our service, generating a leaderboard. We use this simulator to compare different versions of the predictor and to determine the smallest time window that we can perform forecasts without compromising accuracy.

Our service runs inside Docker containers and takes advantage of Nvidia GPUs. It is assumed that this code will run in a Linux environment with Nvidia drivers and Docker installed. Below are two sections, one with a quick start tutorial and another that describes what each directory contains and how they work.

## Quickstart

You may want to run the predictor in one of two ways: 1) as a stand-alone service or 2) as a simulation that evaluates the predictor. Below we describe both:

### 1) Forecasting Service
This is the first option, where it just launches the service with an HTTP server that accepts connections. To launch the forecast service, do the following from the root of this repository:
```sh
cd service
./run_server_container.sh
```
This will launch a Docker container running in the background, with an HTTP server. You can find more details in the Readme.md inside the folder [service](service). Basically, this service will receive notifications of function invocations and compute the leaderboard upon request.


### 2) Simulation and Evaluation of the Forecasting Service
In this second option, we explain how to run an experiment that simulates and plots the results. This simulation will launch our forecasting service, then use the traces from the Azure 2019 dataset to realistically notify the service with function invocations. After this, it will request the service to compute the current leaderboard. This process will be performed for multiple different predictors and for different time windows. In the end, the leaderboards are passed to a Python script that will measure how accurate each leaderboard was relative to the real trace costs. To run and plot this simulation, first make sure you have downloaded the Azure dataset by doing the following from the root of this repository:
```sh
cd azure-dataset
./download_dataset.sh
cd ..
```
All the scripts assume that the dataset is located in `azure-dataset/input/`. Then you can run the simulation by doing the following:
```sh
cd simulator
./run_simulator.sh
cd ..
```

This may take some time to run. It will launch the service and provide it with multiple traces, and in the end, request a leaderboard of which function traces will be more costly in the future. You can find more details in [simulator](simulator). After the simulation has ended, the directory containing the resulting leaderboard will be printed in the command line. Now you need to copy the contents of this directory to the plots directory and plot the figure. To do this, run the commands below, replacing the `username` and `randomID` with the corresponding directory that was printed to the command line at the end of the simulation, like this:
```sh
cp simulator/results/forcast-username-randomID/* plots/results/comparation/
cd plots/
python3 plot_cost_comparation.py
```

This will generate a figure in the local directory, named `models_comparation.png`. You can adjust experiment parameters by modifying the `run_simulator.sh` and then adjusting `plot_cost_comparation.py` to plot these changes correctly.




## Directories Description

The repository is split into several directories, each one responsible for a different part of the complete service. Specific details of each directory:

- [data_manager](data_manager) this folder contains the `trace_generator.py` script that is used by all other components of this repository, it creates an abstraction to deal with the Azure dataset. This Python script is responsible for transforming the raw data from the dataset into a Pandas DataFrame so that it can be used by other components. An important note, each time a trace is accessed for the first time, a `.csv` file is created in `data_manager/data/complete_traces/traces_datapoints/`, since there are 70,000 different traces, this directory can grow to multiple GBs. This `.csv` file is an intermediate representation of the trace for faster access if accessed later. Finally, you can also find the `sinusoidal_detector.py` script inside this directory. This script has an explanation inside; the goal was to find a way to detect if a given trace is sinusoidal or not. This is ongoing work and is important for clustering the dataset functions to improve the process of finding similar function traces in the predictor. This script will try to categorize a number of traces, defined by the `number_of_traces` variable. You can observe the generated output figure in `data_manager/data/complete_traces/traces_plots/`

- [plots](plots) this directory contains the script `plot_cost_comparation.py` that is used to generate a figure that compares the cost of different predictors. This script requires that the leaderboards be located in`plots/results/comparation/`,, and depending on the parameters of each experiment, it may also be required to adjust the parameters inside the Python script, such as `simulation_start`, `simulation_end`, `model_types`, `prediction_window` and others. 

- [predictor](predictor) this directory contains different predictors that the service may call when building a new leaderboard. These predictors are usually run in parallel by the service. The predictor based on AutoGluon requires the models to be trained, this is done automatically by the service, which checks if there are trained models, otherwise, it trains them before launching the service. You can find more details about the predictors in the Readme.md inside the folder.

- [service](service) this directory contains the scripts and code that launch the forecasting service. It will run a background HTTP server in Python. You can find more details including the REST API endpoints available in the Readme.md inside the folder. This folder also contains the `cost_function.py` script that is used to compute the cost of the traces prediction to afterward sort the leaderboard.

- [simulator](simulator) this directory contains the `run_simulator.sh` script that launches the forecasting service and then iterates over each trace ID in `simulation_trace_ids.txt` and performs a POST notifying the service of the function invocations. This is performed over multiple time windows, defined inside the script, and for multiple predictors. More details of the available predictors can be found in [predictor](predictor). All the leaderboards resulting from running the script are stored inside `simulator/results/`. This script also prints to the command line the locations of the generated output.

## Future Improvements
1. The location of the Azure dataset is hardcoded in multiple places, it assumes always that it is in `azure-dataset/input/.`
2. The clustering for similar functions has not been implemented. It requires some way to categorize if a given function is sinusoidal or not, something I have not yet been able to achieve.