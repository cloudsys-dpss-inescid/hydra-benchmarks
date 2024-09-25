# Simulator

This directory contains a simple simulator, the script `run_simulator.sh`, which launches the forecast service, uploads multiple traces, and requests the leaderboard. At the end, it plots the performance of the simulation. All of this is done automatically. You can modify the script to change various parameters, such as `WINDOW_SIZE`, which represents the number of minutes of data uploaded for each function before computing the leaderboard. The larger the window, the more data is available, resulting in more accurate forecasts. However, the longer you wait, the less performance gain you achieve from possible AoT compilation. 

You can also change the predictor used by modifying the `PREDICTOR_MODE` variable, or adjust how many leaderboards are computed during the simulation using the `NUMBER_OF_LEADERBOARDS` variable.

All the traces uploaded are listed in the file `simulation_trace_ids.txt`. Currently, this file contains only a few traces, as it has been used for debugging. Ideally, you would want all traces in the file, but this would take several hours to process. We have tested with 10,000 functions in the file `simulation_trace_ids_10k.txt`, which took around 8 hours on Vitamina 04.

Final note: the plots are located in the `plot/` directory, and logs are in `simulator/debug/`.
