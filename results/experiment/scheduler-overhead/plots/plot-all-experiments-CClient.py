
#!/usr/bin/env python

import results
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from datetime import datetime, timedelta



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


def makeFig(file_name, title, GC_type):

    plt.rcParams.update({'font.size': 12})



    experiment_lines = [1,2,4,8,16,32,64,128,256,512,1024]
    #experiment_lines = [2]
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        print("Processing experiment with " + str(exp) + " threads")
        fig, ax = plt.subplots(4, figsize=(20, 10))


        #######################
        #### Plot clean data
        #######################
        file_path = "../results/java/CClientClean/gv-" + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

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

        file_path = "../results/java/CClientBenchmark/gv-" + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"

        #CPU usage points
        CPU_reading_timestamp, CPU_usage = results.processCpuUsage( results.read_cpu_usage(file_path) )

        ### GC points
        if(GC_type != "G1"):
            Incremental_GC, Full_GC = results.get_GC_datapoints(file_path)

        #CPerf and context swricth points
        results.process_perf_record_data(file_path)
        context_switches_timestamps = results.get_context_switches_datapoints(file_path)
        array_counter, array_timestamp = process_context_switches_datapoints(context_switches_timestamps, 1000) #delta_interval is in miliseconds
        #ctx_dictionary = Counter(context_switches_timestamps)



     


        first_timestamp = float('inf')
        timestamp_left = 0
        timestamp_rigth = float('inf')
        max_latency = 0

        for thread_id in range(exp):
            
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)

            #frist thread show individual points
            if(thread_id == 0):
                ax[1].scatter( timestamp_array, latency_array, s=5, color ="black" , zorder=200, label="Single thread trace")

            ax[1].plot(timestamp_array, latency_array, alpha=0.2, zorder=-1)#, label= 'thread ' + str(thread_id) ) 

            first_timestamp = min(first_timestamp, timestamp_array[0])
            timestamp_left = max(timestamp_left, timestamp_array[0])
            timestamp_rigth = min(timestamp_rigth, timestamp_array[-1])
            max_latency = max(max_latency, max(latency_array))



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


        if(GC_type != "G1"):
            ax[1].scatter( Incremental_GC, np.full(len(Incremental_GC), max_latency*0.8), s=5, color ="blue" , zorder=200, label="Incremental GC")
            ax[1].scatter( Full_GC, np.full(len(Full_GC), max_latency*0.6), s=5, color ="green" , zorder=200, label="Full GC")

        ax[1].set_ylabel('Latency (ms)')
        ax[1].set_xlabel('Linux timestamp over time (ms)')
        #ax[1].set_ylim([-1, 25])

        ax[1].legend(ncol=5, loc='upper center')
        ax[1].set_title(title+ ", "+ str(exp)+ " threads/CS (throughput = " + str(round(exp_throughput)) + " op/s , duration = " + str(elipsed_time_ms) + " ms, work = " + str( len(timestamp_array) ) + ")" ) 
        
        fig.tight_layout()

        #plt.savefig("all_runtimes/CClient/" + file_name + "-" + str(exp) + "CS.pdf", bbox_inches='tight')
        plt.savefig("all_runtimes/CClient/raw-cpu-" + file_name + "-" + str(exp) + "CS.png", bbox_inches='tight')
        









    
                                                                                    #Y latency min , max, SLA
makeFig( "httprequest", "HTTP request app", "G1")
#makeFig( isolate_http_benchmark_path, "file-hashing", "File hashing app",  1, 4000, 100)
#makeFig( isolate_http_benchmark_path, "sleep", "Sleep app",  1, 4000, 100)




