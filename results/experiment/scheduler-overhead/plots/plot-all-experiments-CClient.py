
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
    latency_array_GC = []

    for idx_latency, current_timestamp_latency in enumerate(timestamp_array):
        

        GC_timestamp_start = Pause_Young_GC[idx_GC] - 200
        GC_timestamp_end = GC_timestamp_start + Pause_duration[idx_GC] + 200
        if current_timestamp_latency >= GC_timestamp_start and current_timestamp_latency <= GC_timestamp_end:
            latency_array_GC.append(latency_array[idx_latency])
            latency_array[idx_latency] = -5
            #print("idx_latency: " + str(idx_latency) )
            #print("current_timestamp_latency: " + str(current_timestamp_latency) )
            #print("GC_timestamp_start:        " + str(GC_timestamp_start) )
            #print("GC_timestamp_end:          " + str(GC_timestamp_end) )
        
        if current_timestamp_latency > GC_timestamp_end:
            idx_GC = min(idx_GC+1, len(Pause_Young_GC) - 1)

 
 
    return timestamp_array, latency_array, latency_array_GC

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



    experiment_lines = [1,2,4,8,16,32,64,128,256,512,1024]
    experiment_lines = [1024]
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        print("Processing experiment with " + str(exp) + " threads")
        fig, ax = plt.subplots(6, figsize=(20, 10))


        #######################
        #### Plot clean data
        #######################
        file_path = dir_clean_data + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

        timestamp_left = 0
        timestamp_rigth = float('inf')

        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)

            #frist thread show individual points
            if(thread_id == 0):
                ax[0].scatter( timestamp_array, latency_array, s=5, color ="black" , zorder=200, label="Single thread trace")

            ax[0].plot(timestamp_array, latency_array, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            timestamp_left = max(timestamp_left, timestamp_array[0])
            timestamp_rigth = min(timestamp_rigth, timestamp_array[-1])



        exp_throughput = 0
        #compute throughput
        for thread_id in range(exp):

            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)            

            exp_throughput += results.get_thread_throughput(timestamp_left, timestamp_rigth, timestamp_array)

        
        elipsed_time_ms = round(timestamp_rigth - timestamp_left)
        ax[0].legend(ncol=5, loc='upper center')
        ax[0].set_title(title+ ", "+ str(exp)+ " threads/CS (throughput = " + str(round(exp_throughput)) + " op/s , duration = " + str(elipsed_time_ms) + " ms, work = " + str( len(timestamp_array) ) + ") *Clean Run*" )






        #################################
        #### Plot verbose benchamark data
        #################################

        file_path = dir_benchmark + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

        #CPU usage points
        CPU_reading_timestamp, CPU_usage = results.processCpuUsage( results.read_cpu_usage(file_path) )

        ### GC points
        if(GC_type != "G1"):
            Incremental_GC, Full_GC = results.get_GC_datapoints(file_path)
        else:
            Pause_Young_GC, Pause_duration = results.get_GC_G1_datapoints(file_path)

        #CPerf and context swricth points
        results.process_perf_record_data(file_path)
        context_switches_timestamps = results.get_context_switches_datapoints(file_path)
        array_counter, array_timestamp = process_context_switches_datapoints(context_switches_timestamps, 1000) #delta_interval is in miliseconds
        #ctx_dictionary = Counter(context_switches_timestamps)



     


        first_timestamp = float('inf')
        timestamp_left = 0
        timestamp_rigth = float('inf')
        max_latency = 0

        total_latency_sum = 0
        total_datapoints_count = 0
        
        all_latency_array_GC= []

        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)
            
            cut_initial_points = 1000
            latency_array = latency_array[cut_initial_points:]
            timestamp_array = timestamp_array[cut_initial_points:]
                        
            total_datapoints_count += len(latency_array)
            total_latency_sum += sum(latency_array)


            #frist thread show individual points
            if(thread_id == 0):
                ax[1].scatter( timestamp_array, latency_array, s=5, color ="black" , zorder=200, label="Single thread trace")

            ax[1].plot(timestamp_array, latency_array, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            ### Plot clean data points
            if(GC_type == "G1"):
                timestamp_array_clean, latency_array_clean, latency_array_GC = clean_GC_from_datapoints(Pause_Young_GC, Pause_duration, timestamp_array, latency_array)
                all_latency_array_GC += latency_array_GC
                cut_initial_points = 1000
                latency_array_clean = latency_array_clean[cut_initial_points:]
                timestamp_array_clean = timestamp_array_clean[cut_initial_points:]
                ax[4].plot(timestamp_array_clean, latency_array_clean, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 
            


            first_timestamp = min(first_timestamp, timestamp_array[0])
            timestamp_left = max(timestamp_left, timestamp_array[0])
            timestamp_rigth = min(timestamp_rigth, timestamp_array[-1])
            max_latency = max(max_latency, max(latency_array))

        mean_latency = total_latency_sum / total_datapoints_count
        ax[1].axhline(y=mean_latency, color='red', linestyle='-', linewidth=1.5, label='Mean Latency: '+ str(mean_latency) )
        #ax[1].set_ylim(0, 2.5 * mean_latency)
        
        x = np.sort(all_latency_array_GC) 
        y = np.arange(len(all_latency_array_GC)) / float(len(all_latency_array_GC))        
        
        gc_index  = get_index_GC_points(all_latency_array_GC)
        
        ax[5].scatter(x, y, s=5, color ="red", label="Context switches")
        ax[5].scatter(x[gc_index:], y[gc_index:], s=5, color ="green")







        exp_throughput = 0
        #compute throughput
        for thread_id in range(exp):

            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)            

            exp_throughput += results.get_thread_throughput(timestamp_left, timestamp_rigth, timestamp_array)

        
        ############## CPU usage
        #clean the CPU_reading_timestamp array for cpu reading before the threads where running
        index = next((i for i, ts in enumerate(CPU_reading_timestamp) if ts > first_timestamp), len(CPU_reading_timestamp))
        # Slice both arrays based on the found index
        CPU_usage = CPU_usage[index:]
        CPU_reading_timestamp = CPU_reading_timestamp[index:]
        elipsed_time_ms = round(timestamp_rigth - timestamp_left)

        ax[2].plot( CPU_reading_timestamp, CPU_usage , marker=".", markersize=5) 
        ax[2].set_ylabel('CPU usage (%), $\\Delta$ 0.5s each')
        ax[2].set_ylim([0, 100])
        ax[2].legend(ncol=5, loc='upper center')



        ############# Perf points
        #clean the perf array for scheduler readings before the threads where running
        index = next((i for i, ts in enumerate(array_timestamp) if ts > first_timestamp), len(array_timestamp))
        array_counter = array_counter[index:]
        array_timestamp = array_timestamp[index:]                
        ax[3].scatter( array_timestamp, array_counter, s=5, color ="red", label="Context switches")
        ax[3].set_ylabel("Number of occurrences\nin a 1s interval")

        
        ############# GC points
        if(GC_type != "G1"):
            ax[1].scatter( Incremental_GC, np.full(len(Incremental_GC), max_latency*0.8), s=5, color ="blue" , zorder=200, label="Incremental GC")
            ax[1].scatter( Full_GC, np.full(len(Full_GC), max_latency*0.6), s=5, color ="green" , zorder=200, label="Full GC")
        else:
            ax[1].scatter( Pause_Young_GC, np.full(len(Pause_Young_GC), max_latency*0.6), s=10, color ="red" , zorder=200, label="G1 Evacuation Pause")

            
        ax[1].set_ylabel('Latency (ms)')
        ax[1].set_xlabel('Linux timestamp over time (ms)')
        #ax[1].set_ylim([-1, 25])

        ax[1].legend(ncol=5, loc='upper center')
        ax[1].set_title(title+ ", "+ str(exp)+ " threads/CS (throughput = " + str(round(exp_throughput)) + " op/s , duration = " + str(elipsed_time_ms) + " ms, work = " + str( len(timestamp_array) ) + ")" ) 
        
        plt.subplots_adjust(hspace=1)

        fig.tight_layout()

        #plt.savefig("all_runtimes/CClient/" + file_name + "-" + str(exp) + "CS.pdf", bbox_inches='tight')
        plt.savefig(dir_plots + file_name + "-" + str(exp) + "CS.png", bbox_inches='tight')
        









    
                                                                                    #Y latency min , max, SLA
makeFig( "httprequest", "HTTP request app", "G1")
#makeFig( isolate_http_benchmark_path, "file-hashing", "File hashing app",  1, 4000, 100)
#makeFig( isolate_http_benchmark_path, "sleep", "Sleep app",  1, 4000, 100)




