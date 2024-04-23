#!/usr/bin/env python
import results
import matplotlib.pyplot as plt

import numpy as np
from collections import Counter
from datetime import datetime, timedelta

dir_benchmark = "../results/java/CClientBenchmark/gv-"
dir_clean_data = "../results/java/CClientClean/gv-"
dir_plots = "perf-figs/"

first_values_cut = 600
X_axis_offset = 200 # This value is only used to ajust the X axis on the plots, the 200 is to have some extra space 
_markersize = 20

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

#I need a costum function, becasuse the ones from Python do an avarage when two middle values when even amount of elements are provided and I need existing value for indexing
def median_index(lst):
    
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    
    return index

def get_index_GC_in_latencies(target_value, latency_array):

    for indx, current_value in enumerate(latency_array):
        if  current_value >= target_value:
            return indx
    return -1

def get_index_by_latency(target, latency_index, latency_array):


    for idx, value in enumerate(latency_array):

        if( value == target ):
            return idx + latency_index

    return latency_index

def clean_datapoints_from_GC(GC_timestamps, GC_pause_duration, timestamp_array, latency_array):

    idx_GC = 0
    latency_array_GC = []
    cut_initial_points = 1000
    cut_off_set_max = 401

    #when theres no GC points, just cut the inicial points that usualy have some noise
    if len(GC_timestamps) == 0:
        latency_array_clean = latency_array[cut_initial_points:]
        timestamp_array_clean = timestamp_array[cut_initial_points:]
        return timestamp_array_clean, latency_array_clean

    elif len(GC_timestamps) == 1:
        latency_index = get_index_GC_in_latencies(GC_timestamps[0] + cut_off_set_max, timestamp_array) 
        latency_array_clean = latency_array[latency_index:]
        timestamp_array_clean = timestamp_array[latency_index:]        
        return timestamp_array_clean, latency_array_clean
    
    elif len(GC_timestamps) >= 3:

        GC_median_idx = median_index(GC_timestamps)
        l_GC_median_idx = GC_median_idx - 1
        r_GC_median_idx = GC_median_idx  + 1



        median_latency_index = get_index_GC_in_latencies(GC_timestamps[GC_median_idx], timestamp_array) 
        l_latency_index = get_index_GC_in_latencies(GC_timestamps[l_GC_median_idx], timestamp_array) 
        r_latency_index = get_index_GC_in_latencies(GC_timestamps[r_GC_median_idx], timestamp_array) 


        l_latency_array_clean = latency_array[l_latency_index:median_latency_index]
        r_latency_array_clean = latency_array[median_latency_index:r_latency_index]

        l_max = max(l_latency_array_clean)
        r_max = max(r_latency_array_clean)


        l_index = get_index_by_latency(l_max, l_latency_index, l_latency_array_clean) + 30
        r_index = get_index_by_latency(r_max, median_latency_index, r_latency_array_clean) - 30


        latency_array_clean = latency_array[l_index:r_index]
        timestamp_array_clean = timestamp_array[l_index:r_index]

        return timestamp_array_clean, latency_array_clean


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



def makeFig(file_name, title, GC_type, experiment_lines):

    plt.rcParams.update({'font.size': 30})
    
    perf_avg_holder = []
    lat_avg_holder = []
    lat_p90_holder = []
    lat_p95_holder = []
    lat_p96_holder = []
    lat_p97_holder = []
    lat_p98_holder = []
    lat_p99_holder = []
        
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        print("Processing experiment with " + str(exp) + " threads")
        fig, ax = plt.subplots(2, figsize=(20, 25))







        #################################
        #### Plot verbose benchamark data
        #################################

        file_path = dir_benchmark + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"
        
        experience_start_time, from_boot_to_reference = results.get_starting_time(file_path)

        ### GC points
        Pause_Young_GC, Pause_duration, Isolate_GCs, number_of_reading_erros, Incremental_GC, Full_GC = results.get_GC_G1_datapoints(file_path, experience_start_time)

        #CPerf and context swricth points
        array_counter = []
        array_timestamp = []
        try:
            #results.process_perf_record_data(file_path)
            results.process_perf_sched_data(file_path)            
            context_switches_timestamps = results.get_context_switches_datapoints(file_path, experience_start_time)
            array_counter, array_timestamp = process_context_switches_datapoints(context_switches_timestamps, 100) #delta_interval is in miliseconds
        #ctx_dictionary = Counter(context_switches_timestamps)
        except Exception as e:
            print("Error processing perf ")

        
        #Latencies points
        first_timestamp = float('inf')
        last_timestamp = 0
        timestamp_left = 0
        timestamp_rigth = float('inf')
        timestamp_left_clean = 0
        timestamp_rigth_clean = float('inf')        
        max_latency = 0
        max_latency_clean = 0

        total_latency_sum = 0
        total_datapoints_count = 0
        all_clean_latency_array = []
        


        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id, experience_start_time)
                                    

            ### Plot clean data points
            if( len(Incremental_GC) + len(Full_GC) > 0 ):
                all_GC_timestamps = Incremental_GC + Full_GC
                timestamp_array_clean, latency_array_clean = clean_datapoints_from_GC(all_GC_timestamps, Pause_duration, timestamp_array, latency_array)
            else:
                timestamp_array_clean, latency_array_clean = clean_datapoints_from_GC(Pause_Young_GC, Pause_duration, timestamp_array, latency_array)

            all_clean_latency_array = all_clean_latency_array + latency_array_clean






        #perf plot, I have to change this to only make the avg on the clean data/no GC        
        perf_avg_holder.append( np.average(array_counter) )

        lat_avg_holder.append( np.average(all_clean_latency_array) )
        lat_p90_holder.append( np.percentile(all_clean_latency_array,90) )
        lat_p95_holder.append( np.percentile(all_clean_latency_array,95) )
        lat_p96_holder.append( np.percentile(all_clean_latency_array,96) )
        lat_p97_holder.append( np.percentile(all_clean_latency_array,97) )
        lat_p98_holder.append( np.percentile(all_clean_latency_array,98) )
        lat_p99_holder.append( np.percentile(all_clean_latency_array,99) )










    
    ax[0].plot( experiment_lines, lat_avg_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax[0].plot( experiment_lines, lat_p90_holder, marker=".", markersize=_markersize, label = 'percentil 90')
    ax[0].plot( experiment_lines, lat_p95_holder, marker=".", markersize=_markersize, label = 'percentil 95')    
    #ax[0].plot( experiment_lines, lat_p96_holder, marker=".", markersize=_markersize, label = 'percentil 96')    
    ax[0].plot( experiment_lines, lat_p97_holder, marker=".", markersize=_markersize, label = 'percentil 97')    
    #ax[0].plot( experiment_lines, lat_p98_holder, marker=".", markersize=_markersize, label = 'percentil 98')    
    ax[0].plot( experiment_lines, lat_p99_holder, marker=".", markersize=_markersize, label = 'percentil 99')    
    ax[0].legend(ncol=5, loc='upper center', bbox_to_anchor=(0.5, 1.2))
    ax[0].set_ylabel('Request latency (ms)')
    ax[0].set_xlabel('Concurrent sandboxes ≡ client threads')    
    ax[0].set_title("Latency without GCs")
    
    
    ax[1].plot( experiment_lines, perf_avg_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax[1].legend(ncol=5, loc='upper center', bbox_to_anchor=(0.5, 1.2))
    ax[1].set_ylabel('# perf events ')
    ax[1].set_xlabel('Concurrent sandboxes ≡ client threads')    
    ax[1].set_title("Perf script | grep sched_switch")

    fig.tight_layout()

    plt.subplots_adjust(hspace=0.3)
    
    #plt.savefig("all_runtimes/CClient/" + file_name + "-" + str(exp) + "CS.pdf", bbox_inches='tight')
    plt.savefig(dir_plots + "perf_values.png", bbox_inches='tight')
        









experiment_lines = [1,2,4,8,16,32,64,128,256,512]
#experiment_lines = [1,2,4]



#makeFig( "httprequest", "HTTP request app", "G1", experiment_lines)
makeFig( "dbreader", "Memcached request app", "G1", experiment_lines)






