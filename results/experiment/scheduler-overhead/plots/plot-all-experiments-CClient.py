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
dir_plots = "all_runtimes/CClient/raw-cpu-"

first_values_cut = 600
X_axis_offset = 200 # This value is only used to ajust the X axis on the plots, the 200 is to have some extra space 

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

    plt.rcParams.update({'font.size': 18})
    
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        print("Processing experiment with " + str(exp) + " threads")
        fig, ax = plt.subplots(8, figsize=(20, 25))


        #######################
        #### Plot clean data
        #######################
        file_path = dir_clean_data + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"
        
        experience_start_time, from_boot_to_reference = results.get_starting_time(file_path)
        timestamp_left = 0
        timestamp_rigth = float('inf')
        total_latency_sum = 0
        total_datapoints_count = 0

        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id, experience_start_time)
            
            total_datapoints_count += len(latency_array)
            total_latency_sum += sum(latency_array)

            #frist thread show individual points
            if(thread_id == 0):
                ax[0].scatter( timestamp_array, latency_array, s=5, color ="black" , zorder=200, label="Single thread trace")

            ax[0].scatter(timestamp_array, latency_array, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            timestamp_left = max(timestamp_left, timestamp_array[0])
            timestamp_rigth = min(timestamp_rigth, timestamp_array[-1])


        exp_throughput = 0
        #compute throughput
        for thread_id in range(exp):

            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id, experience_start_time)            

            exp_throughput += results.get_thread_throughput(timestamp_left, timestamp_rigth, timestamp_array)


        avg_latency = round(total_latency_sum / total_datapoints_count,2)
        ax[0].axhline(y=avg_latency, color='red', linestyle='-', linewidth=1.5, label='Avarage Latency: '+ str(avg_latency)+" ms" )

        elipsed_time_ms = round(timestamp_rigth - timestamp_left)
        ax[0].legend(ncol=5, loc='upper center')

        ax[0].set_title(title+ ", "+ str(exp)+ " threads/CS (throughput = " + str(round(exp_throughput)) + " op/s , duration = " + str(elipsed_time_ms) + " ms, work = " + str( len(timestamp_array) ) + ") *Clean Run*" )
        ax[0].set_xlabel('Linux timestamp over time (ms)')






        #################################
        #### Plot verbose benchamark data
        #################################

        file_path = dir_benchmark + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"
        
        experience_start_time, from_boot_to_reference = results.get_starting_time(file_path)
        #CPU usage points
        CPU_reading_timestamp, CPU_usage = results.processCpuUsage( results.read_cpu_usage(file_path, experience_start_time) )

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
                                    
            total_datapoints_count += len(latency_array)
            total_latency_sum += sum(latency_array)

            #frist thread show individual points
            if(thread_id == 0):
                ax[1].scatter( timestamp_array, latency_array, s=5, color ="black" , zorder=200, label="Single thread trace")

            ax[1].scatter(timestamp_array, latency_array, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            ### Plot clean data points
            if( len(Incremental_GC) + len(Full_GC) > 0 ):
                all_GC_timestamps = Incremental_GC + Full_GC
                timestamp_array_clean, latency_array_clean = clean_datapoints_from_GC(all_GC_timestamps, Pause_duration, timestamp_array, latency_array)
            else:
                timestamp_array_clean, latency_array_clean = clean_datapoints_from_GC(Pause_Young_GC, Pause_duration, timestamp_array, latency_array)

            ax[1].axvline(x=timestamp_array_clean[0], color='lime', linestyle='-', linewidth=1.5)
            ax[1].axvline(x=timestamp_array_clean[-1], color='lime', linestyle='-', linewidth=1.5)


            ax[4].scatter(timestamp_array_clean, latency_array_clean, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            ax[6].scatter(timestamp_array[:first_values_cut], latency_array[:first_values_cut], alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 
            ax[7].scatter(timestamp_array[:first_values_cut], latency_array[:first_values_cut], alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            all_clean_latency_array += latency_array_clean



            first_timestamp = min(first_timestamp, timestamp_array[0])
            last_timestamp = max(last_timestamp, timestamp_array[-1])
            timestamp_left = max(timestamp_left, timestamp_array[0])
            timestamp_rigth = min(timestamp_rigth, timestamp_array[-1])
            timestamp_left_clean = max(timestamp_left_clean, timestamp_array_clean[0])
            timestamp_rigth_clean = min(timestamp_rigth_clean, timestamp_array_clean[-1])            
            max_latency = max(max_latency, max(latency_array))
            max_latency_clean = max(max_latency_clean, max(latency_array_clean))

        avg_latency = round(total_latency_sum / total_datapoints_count,2)
        ax[1].axhline(y=avg_latency, color='red', linestyle='-', linewidth=1.5, label='Avarage Latency: '+ str(avg_latency)+" ms" )
        #ax[1].set_ylim(0, 2.5 * avg_latency)
        
        x = np.sort(all_clean_latency_array) 
        y = np.arange(len(all_clean_latency_array)) / float(len(all_clean_latency_array))        
                
        ax[5].scatter(x, y, s=5, color ="red", label="CDF")
        ax[5].set_title("Latency CDF for time window without Hydra GC")
        ax[5].set_ylabel('%')
        ax[5].set_xlabel('Latency (ms)')

        ### Try to calculate the percenty of this free GC data
        possible_limite = 20 #miliseconds
        arr = np.array(x)
        split_arr = np.where(arr > possible_limite)[0]
        data_perentage = ( 100 * len(split_arr) ) / len(x)
        print(" Percentage of the data cut in " + str(possible_limite) + "ms is " + str(data_perentage) )


        #print("timestamp_left: " + str(timestamp_left) + " timestamp_rigth: " + str(timestamp_rigth))

        exp_throughput = 0
        #compute throughput
        for thread_id in range(exp):

            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id, experience_start_time)            

            exp_throughput += results.get_thread_throughput(timestamp_left, timestamp_rigth, timestamp_array)

        
        ############## CPU usage
        #clean the CPU_reading_timestamp array for cpu reading before the threads where running
        #index = next((i for i, ts in enumerate(CPU_reading_timestamp) if ts > first_timestamp), len(CPU_reading_timestamp))
        # Slice both arrays based on the found index
        #CPU_usage = CPU_usage[index:]
        #CPU_reading_timestamp = CPU_reading_timestamp[index:]
        elipsed_time_ms = round(timestamp_rigth - timestamp_left)

        ax[2].plot( CPU_reading_timestamp, CPU_usage , marker=".", markersize=5) 
        ax[2].set_ylabel('CPU usage (%),\n $\\Delta$ 0.2s each')
        ax[2].set_ylim([0, 100])
        #ax[2].set_xlim(first_timestamp - X_axis_offset, last_timestamp + X_axis_offset )
        ax[2].set_xlim(0, last_timestamp + X_axis_offset )
        ax[2].set_title("CPU usage")
        ax[2].set_xlabel('Linux timestamp over time (ms)')

        ############# Perf points
        #clean the perf array for scheduler readings before the threads where running
        #index = next((i for i, ts in enumerate(array_timestamp) if ts > first_timestamp), len(array_timestamp))
        #array_counter = array_counter[index:]
        #array_timestamp = array_timestamp[index:]
        if( len(array_timestamp) > 0):                 
            ax[3].scatter( array_timestamp, array_counter, s=5, color ="red", label="Context switches")
            #ax[3].scatter( context_switches_timestamps, np.arange(len(context_switches_timestamps)), s=5, color ="red", label="Context switches")
            ax[3].set_ylabel("Number of occurrences\nin a 0.1s interval")
            #ax[3].set_title("Perf measuring context switches")
            ax[3].set_title("Perf measuring all sched events")
            #ax[3].set_xlim(first_timestamp - X_axis_offset, last_timestamp + X_axis_offset)
            ax[3].set_xlim(0, last_timestamp + X_axis_offset)
            ax[3].set_yscale('log')
        
        ############# GC points  G1
        if(len(Pause_Young_GC) > 0):
            ax[1].scatter( Pause_Young_GC, np.full(len(Pause_Young_GC), max_latency*0.6), s=10, color ="red" , zorder=200, label="G1 Evacuation Pause event")
        if(len(Isolate_GCs) > 0):
            ax[1].scatter( Isolate_GCs, np.full(len(Isolate_GCs), max_latency*0.8), s=10, color ="blue" , label="Isolate GC event " + str(len(Isolate_GCs)) +  "/" + str(number_of_reading_erros+len(Isolate_GCs)))
        #ax[1].set_xlim(timestamp_left, timestamp_rigth*1.0000001 )
        #ax[1].set_xlim(first_timestamp - X_axis_offset, last_timestamp + X_axis_offset)

        ############# GC points normal GC
        if(len(Incremental_GC) > 0):
            ax[1].scatter( Incremental_GC, np.full(len(Incremental_GC), max_latency*0.8), s=5, color ="blue" , zorder=200, label="Incremental GC event", marker="v")
        if(len(Full_GC) > 0):
            ax[1].scatter( Full_GC, np.full(len(Full_GC), max_latency*0.6), s=5, color ="green" , zorder=200, label="Full GC event", marker="v")
 
        ax[1].set_xlim(0, last_timestamp + X_axis_offset)
        
        ##this is failing when I use perf because of the overhead
        remove_above_limit = 50
        all_clean_latency_array = np.array(all_clean_latency_array)
        below_limit_values = all_clean_latency_array[all_clean_latency_array < remove_above_limit]        
        top_y = max(below_limit_values)
        
        ax[4].scatter( Isolate_GCs, np.full(len(Isolate_GCs), max_latency_clean*0.6), s=10, color ="blue" , zorder=200, label="Isolate GC")
        ax[4].set_xlim(timestamp_left_clean, timestamp_rigth_clean)
        ax[4].set_ylim(0, top_y)
        ax[4].set_title("Latency and Isolate GCs in time window without Hydra GC")
        ax[4].set_ylabel('Latency (ms)')
        ax[4].set_xlabel('Linux timestamp over time (ms)')



        ax[6].set_title("Just the first values")
        xmin, xmax = ax[6].get_xlim()
        ax[6].scatter( Pause_Young_GC, np.full(len(Pause_Young_GC), max_latency_clean*0.5), s=10, color ="red" , zorder=200, label="G1 Evacuation Pause")
        ax[6].scatter( Isolate_GCs, np.full(len(Isolate_GCs), max_latency_clean*0.6), s=10, color ="blue" , zorder=200, label="Isolate GC")
        ax[6].set_ylim(0,max_latency_clean)
        ax[6].set_xlim(xmin,xmax)

        ax[7].set_title("Just the first values, no Y limit")
    
        ax[1].set_ylabel('Latency (ms)')
        ax[1].set_xlabel('Linux timestamp over time (ms)')
        #ax[1].set_ylim([-1, 25])

        ax[1].legend(ncol=5, loc='upper right', bbox_to_anchor=(0.95, 1.38) )
        ax[1].set_title(title+ ", "+ str(exp)+ " threads/CS (throughput = " + str(round(exp_throughput)) + " op/s , duration = " + str(elipsed_time_ms) + " ms, work = " + str( len(timestamp_array) ) + ")" ,  y=1.28)
        

        fig.tight_layout()

        plt.subplots_adjust(hspace=1)
        
        #plt.savefig("all_runtimes/CClient/" + file_name + "-" + str(exp) + "CS.pdf", bbox_inches='tight')
        plt.savefig(dir_plots + file_name + "-" + str(exp) + "CS.png", bbox_inches='tight')
        









experiment_lines = [1,2,4,8,16,32,64,128,256,512]
#experiment_lines = [512]



#makeFig( "httprequest", "HTTP request app", "G1", experiment_lines)
makeFig( "dbreader", "Memcached request app", "G1", experiment_lines)






