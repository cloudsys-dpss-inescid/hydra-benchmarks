#!/usr/bin/env python
import results
import matplotlib.pyplot as plt

import numpy as np
from collections import Counter
from datetime import datetime, timedelta

dir_benchmark = "../results/java/CClientBenchmark/gv-"
dir_clean_data = "../results/java/CClientClean/gv-"
dir_plots = "perf-figs/"



def transform_points_to_stairs(durations, timestamps, y_value):
    
    y = [0]
    x = [0]
    next_value = 0 

    for idx, element in enumerate(timestamps):

        x.append(element)
        y.append(y_value)

        #just to avoid a situation where the next value has a smaller timestamp than the current ending timestamp
        if(idx < len(timestamps) - 1):
            next_value = min(element + durations[idx] , timestamps[idx + 1])
        else:
            next_value = element + durations[idx]

        x.append(next_value)
        y.append(0)

    x.append(next_value + 1)

    return x, y

def makeFig(file_name, title, experiment_lines):

    for exp in experiment_lines:

        file_path = dir_benchmark + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

        plt.rcParams.update({'font.size': 18})    
        fig, axs = plt.subplots(2, figsize=(20, 10))
        
        #working threads of Hydra
        hydra_timestamps, hydra_wait, hydra_delay, hydra_duration = results.get_timehist_datapoints(file_path,"thread")

        #hydra_timestamps = np.subtract(hydra_timestamps, total_duration) #correct the timestampto the beginning

        run_hydra_timestamps = np.subtract(hydra_timestamps, np.add(np.add(hydra_duration, hydra_delay),hydra_wait)) #correct the timestampto the beginning
        hydra_x, hydra_y = transform_points_to_stairs(hydra_wait, run_hydra_timestamps, 1)
        axs[0].stairs(hydra_y, hydra_x, fill=True, label='Wait time', color='cyan')

        run_hydra_timestamps = np.subtract(hydra_timestamps, np.add(hydra_duration, hydra_delay)) #correct the timestampto the beginning
        hydra_x, hydra_y = transform_points_to_stairs(hydra_delay, run_hydra_timestamps, 1.5)
        axs[0].stairs(hydra_y, hydra_x, fill=True, label='Scheduler delay', color='blue')

        run_hydra_timestamps = np.subtract(hydra_timestamps, hydra_duration) #correct the timestampto the beginning
        hydra_x, hydra_y = transform_points_to_stairs(hydra_duration, run_hydra_timestamps, 2)
        axs[0].stairs(hydra_y, hydra_x, fill=True, label='Hydra running', color='darkgreen')


        #CPU idle cycles
        idle_timestamps, idle_wait, idle_delay, idle_duration = results.get_timehist_datapoints(file_path,"idle")
        
        idle_timestamps = np.subtract(idle_timestamps, idle_duration) #correct the timestampto the beginning
        idle_x, idle_y = transform_points_to_stairs(idle_duration, idle_timestamps, 0.5)
        axs[0].stairs(idle_y, idle_x, fill=True, label='CPU idle', color='grey')

        #CDF 
        x = np.sort(hydra_wait) 
        y = np.arange(len(hydra_wait)) / float(len(hydra_wait))
        axs[1].plot(x, y, label= 'Hydra wait time'  , color="cyan")         
        
        x = np.sort(hydra_delay) 
        y = np.arange(len(hydra_delay)) / float(len(hydra_delay))
        axs[1].plot(x, y, label= 'Scheduler delay'  , color="blue")      

        x = np.sort(hydra_duration) 
        y = np.arange(len(hydra_duration)) / float(len(hydra_duration))
        axs[1].plot(x, y, label= 'Hydra run duration'  , color="darkgreen")  


        axs[0].set_title("Timeline of \"perf sched timehist\" for a single core, only showing Hydra threads")
        axs[1].set_title("Latencies for Hydra threads")


        axs[0].set_xlabel('Linux timestamps (ms)')
        axs[1].set_xlabel('Latency (ms)')
        axs[1].set_ylabel('CDF (%)')
        axs[0].set(ylabel=None)
        axs[0].set_yticklabels([])
        axs[1].set_xscale('log')

        axs[0].legend()
        axs[1].legend()

        plt.subplots_adjust(hspace=1)

        # Displaying Graph
        #plt.show()

        # Displaying Graph
        plt.savefig(dir_plots + "core_time_window.png", bbox_inches='tight')


experiment_lines = [512]

# perf sched timehist --cpu=5 > perf_timehist.log
makeFig( "dbreader", "Memcached request app", experiment_lines)






