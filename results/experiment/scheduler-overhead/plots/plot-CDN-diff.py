
#!/usr/bin/env python

import results
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from datetime import datetime, timedelta

dir_benchmark = "../results/java/CClientBenchmarkNoG1/gv-"
dir_clean_data = "../results/java/CClientCleanNoG1/gv-"
dir_plots = "all_runtimes/CClientNoG1/raw-cpu-"

dir_benchmark = "../results/java/CClientBenchmark/gv-"
dir_clean_data = "../results/java/CClientClean/gv-"
dir_plots = "CDF/plot/CDF-"


dict_colors = {
  1: "#364b9a",
  2: "#4a7bb7",
  4: "#6ea6ce",
  8: "#98cae1",
  16: "#c2e4f0",
  32: "#eaedcd",
  64: "#feda8b",
  128: "#feb467",
  256: "#f67e4b",
  512: "#dd3d2d",
  1024: "#a50026",

}



def process_context_switches_datapoints(array_datapoints, delta_interval):


    interval_deadline = array_datapoints[0] + delta_interval

    array_counter = []
    array_timestamp = []
    counter = 0

    array_timestamp.append(array_datapoints[0])
    for e in array_datapoints:
        
        if e < interval_deadline:
            counter += 1
        else:
            array_counter.append(counter)
            array_timestamp.append(e)

            interval_deadline += delta_interval
            counter = 1
    
    array_counter.append(counter)
    
    return array_counter, array_timestamp


def clean_GC_from_datapoints(Pause_Young_GC, Pause_duration, timestamp_array, latency_array):

    idx_GC = 0

    for idx_latency, current_timestamp_latency in enumerate(timestamp_array):
        

        GC_timestamp_start = Pause_Young_GC[idx_GC] - 200
        GC_timestamp_end = GC_timestamp_start + Pause_duration[idx_GC] + 200
        if current_timestamp_latency >= GC_timestamp_start and current_timestamp_latency <= GC_timestamp_end:
            latency_array[idx_latency] = -5
            #print("idx_latency: " + str(idx_latency) )
            #print("current_timestamp_latency: " + str(current_timestamp_latency) )
            #print("GC_timestamp_start:        " + str(GC_timestamp_start) )
            #print("GC_timestamp_end:          " + str(GC_timestamp_end) )
        
        if current_timestamp_latency > GC_timestamp_end:
            idx_GC = min(idx_GC+1, len(Pause_Young_GC) - 1)

 
 
    return timestamp_array, latency_array

#I need a costum function, becasuse the ones from Python do an avarage when two middle values when even amount of elements are provided and I need existing value for indexing
def median_index(lst):
    
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    
    return index

#this is similar to clustering the points to find GC points
def get_index_GC_points(GC_array):

    GC_array = np.sort(GC_array) 
    y = np.arange(len(GC_array)) / float(len(GC_array))        


    largest_index = 0
    largest_interval = 0

    for current_index in  range(1,len(GC_array)):
        
        current_interval = GC_array[current_index] - GC_array[current_index-1]
        
        if(current_interval > largest_interval):
            largest_interval = current_interval
            largest_index = current_index        

    return largest_index

def get_index_GC_in_latencies(target_value, latency_array):

    for indx, current_value in enumerate(latency_array):
        if  current_value >= target_value:
            return indx
    return -1

def clean_datapoints_from_GC(GC_timestamps, GC_pause_duration, timestamp_array, latency_array):

    idx_GC = 0
    latency_array_GC = []
    cut_initial_points = 1000
    cut_off_set = 400

    #when theres no GC points, just cut the inicial points that usualy have some noise
    if len(GC_timestamps) == 0:
        latency_array = latency_array[cut_initial_points:]
        timestamp_array = timestamp_array[cut_initial_points:]
        return timestamp_array, latency_array

    elif len(GC_timestamps) == 1:
        latency_index = get_index_GC_in_latencies(GC_timestamps[0] + cut_off_set, timestamp_array) 
        latency_array = latency_array[latency_index:]
        timestamp_array = timestamp_array[latency_index:]        
        return timestamp_array, latency_array

    l_GC_median_idx = median_index(GC_timestamps) 
    r_GC_median_idx = l_GC_median_idx + 1
        
    l_GC_timestamp = GC_timestamps[l_GC_median_idx] + cut_off_set
    r_GC_timestamp = GC_timestamps[r_GC_median_idx] - cut_off_set

    l_latency_index = get_index_GC_in_latencies(l_GC_timestamp, timestamp_array) 
    r_latency_index = get_index_GC_in_latencies(r_GC_timestamp, timestamp_array) 

    latency_array = latency_array[l_latency_index:r_latency_index]
    timestamp_array = timestamp_array[l_latency_index:r_latency_index]

    return timestamp_array, latency_array

#this is similar to clustering the points to find GC points
def get_index_GC_points(GC_array):

    GC_array = np.sort(GC_array) 
    y = np.arange(len(GC_array)) / float(len(GC_array))        


    largest_index = 0
    largest_interval = 0

    for current_index in  range(1,len(GC_array)):
        
        current_interval = GC_array[current_index] - GC_array[current_index-1]
        
        if(current_interval > largest_interval):
            largest_interval = current_interval
            largest_index = current_index        

    return largest_index


def makeFig(file_name, title, GC_type):

    plt.rcParams.update({'font.size': 12})


    fig, ax = plt.subplots(5, figsize=(10, 20))

    experiment_lines = [1,2,4,8,16,32,64,128,256,512,1024]
    experiment_lines = [2,64]
    cut_initial_points = 1000
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        print("Processing experiment with " + str(exp) + " threads")


        #######################
        #### Plot clean data
        #######################
        file_path = dir_clean_data + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"


        all_latencies_datapoints = []
        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)
            latency_array = latency_array[cut_initial_points:] #remove iniical noise, it does not count for what we want

            all_latencies_datapoints = all_latencies_datapoints + latency_array

        x = np.sort(all_latencies_datapoints) 
        y = np.arange(len(all_latencies_datapoints)) / float(len(all_latencies_datapoints))
        ax[0].plot(x, y, label= 'thread ' + str(exp)  , color=dict_colors[exp]) 

        ax[0].set_xlim([0, 15])







        #################################
        #### Plot verbose benchamark data
        #################################

        file_path = dir_benchmark + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

        #CPU usage points
        CPU_reading_timestamp, CPU_usage = results.processCpuUsage( results.read_cpu_usage(file_path) )
        
        x = np.sort(CPU_usage) 
        y = np.arange(len(CPU_usage)) / float(len(CPU_usage))
        ax[3].plot(x, y, label= 'thread ' + str(exp) , color=dict_colors[exp]) 


     
        Pause_Young_GC, Pause_duration, Isolate_GCs, number_of_reading_erros = results.get_GC_G1_datapoints(file_path)
        all_latencies_datapoints = []
        all_latencies_datapoints_clean = []

        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)
            _, latency_array_clean = clean_datapoints_from_GC(Pause_Young_GC, Pause_duration, timestamp_array, latency_array)                            
            all_latencies_datapoints_clean = all_latencies_datapoints_clean + latency_array_clean

            latency_array = latency_array[cut_initial_points:] #remove iniical noise, it does not count for what we want
                        
            all_latencies_datapoints = all_latencies_datapoints + latency_array


        x = np.sort(all_latencies_datapoints) 
        y = np.arange(len(all_latencies_datapoints)) / float(len(all_latencies_datapoints))
        ax[1].plot(x, y, label= 'thread ' + str(exp) , color=dict_colors[exp]) 
        ax[2].plot(x, y, label= 'thread ' + str(exp) , color=dict_colors[exp]) 

        

        #gc_index= get_index_GC_points(all_latencies_datapoints)

        x = np.sort(all_latencies_datapoints_clean) 
        y = np.arange(len(all_latencies_datapoints_clean)) / float(len(all_latencies_datapoints_clean))
        ax[4].scatter(x, y, color=dict_colors[exp], marker='.', s=2) 

        ax[4].set_title("Datapoints clean from GC") 


   





    ax[0].set_title("Clean run") 

            
    ax[1].set_ylabel('CDF of requests')
    ax[1].set_xlabel('Request duration (ms)')
    ax[1].set_xlim([0, 15])

    ax[1].legend(ncol=4, loc='lower right')
    ax[1].set_title(title+ ",  52 threads CPU ( work = " + str( len(timestamp_array) ) + ")" ) 
    
    #ax[0].set_xscale('log')
    #ax[1].set_xscale('log')

    ax[3].set_title("CPU Usage CDF") 
    ax[3].set_xlabel('CPU (%) usage')

    fig.tight_layout()

    #plt.savefig("all_runtimes/CClient/" + file_name + "-" + str(exp) + "CS.pdf", bbox_inches='tight')
    plt.savefig(dir_plots + file_name + "-all-CS.png", bbox_inches='tight')
    









    

#makeFig( "httprequest", "HTTP request app", "G1")
makeFig( "dbreader", "Memcached request app", "G1")




