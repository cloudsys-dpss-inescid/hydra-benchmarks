#!/usr/bin/env python

import results
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pylab as pl



_markersize = 8

def printMyLines(text, firstPoints, secondPoints):
    
    print(text)
    print(firstPoints)
    print(secondPoints)
        


def makeFig( file_name, title, experiment_lines):

    #plt.rcParams.update({'font.size': 12})



    cpu_usage_avg_holder = []
    lat_avg_holder = []
    lat_p90_holder = []
    lat_p99_holder = []
    lat_p999_holder = []
    lat_p9999_holder = []
    lat_p99999_holder = []
    lat_p100_holder = []
    
    # Devia de fazer isto pelo results. mas meto isto bonito depois.
    for exp in experiment_lines:
        
        file_path = "../results/java/CClientBenchmark/gv-" + file_name + "-svm-isolate-remote_Cclient_benchmark-"+ str(exp) + "-1-2048/1"
        CPU_reading_timestamp, CPU_usage = results.processCpuUsage( results.read_cpu_usage(file_path) )

        
        first_timestamp = float('inf')

        all_latencies_array = []
        for thread_id in range(exp):
            
            print("aqui:" + str(thread_id) +" file_path " + file_path)
            timestamp_array, latency_array = results.get_latency_datapoints(file_path, thread_id)
            all_latencies_array = all_latencies_array + latency_array
            first_timestamp = min(first_timestamp, timestamp_array[0])

       
        #clean the CPU_reading_timestamp array for cpu reading before the threads where running
        index = next((i for i, ts in enumerate(CPU_reading_timestamp) if ts > first_timestamp), len(CPU_reading_timestamp))
        # Slice both arrays based on the found index
        CPU_usage = CPU_usage[index:]



        cpu_usage_avg_holder.append( np.mean(CPU_usage) )
        
        lat_avg_holder.append( np.average(all_latencies_array) )
        lat_p90_holder.append( np.percentile(all_latencies_array,90) )
        lat_p99_holder.append( np.percentile(all_latencies_array,99) )
        #lat_p999_holder.append( np.percentile(all_latencies_array,99.9) )
        #lat_p9999_holder.append( np.percentile(all_latencies_array,99.99) )
        #lat_p99999_holder.append( np.percentile(all_latencies_array,99.999) )
        #lat_p100_holder.append( np.percentile(all_latencies_array,100) )


    # Create 2x2 sub plots
    gs = gridspec.GridSpec(2, 2,
                           width_ratios=[12, 12],
                           height_ratios=[2, 2]
                           )

    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=2.5, hspace=2.5)

    pl.figure(figsize=(12, 8))

    ax = pl.subplot(gs[0, 0]) # row 0, col 0

    ax.plot( experiment_lines, cpu_usage_avg_holder , marker=".", markersize=_markersize, label = 'Mean value') 
    ax.set_ylabel('CPU usage (%)')
    ax.set_xlabel('Concurrent sandboxes / client threads')

    printMyLines("CPU usage: ", experiment_lines, cpu_usage_avg_holder)


    ax = pl.subplot(gs[0, 1]) # row 0, col 1

    ax.plot( experiment_lines, lat_avg_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax.plot( experiment_lines, lat_p90_holder, marker=".", markersize=_markersize, label = 'p90')
    ax.plot( experiment_lines, lat_p99_holder, marker=".", markersize=_markersize, label = 'p99')
    #ax.plot( experiment_lines, lat_p999_holder, marker=".", markersize=_markersize, label = 'p99.9')
    #ax.plot( experiment_lines, lat_p9999_holder, marker=".", markersize=_markersize, label = 'p99.99')
    #ax.plot( experiment_lines, lat_p99999_holder, marker=".", markersize=_markersize, label = 'p99.999')
    #ax.plot( experiment_lines, lat_p100_holder, marker=".", markersize=_markersize, label = 'p100')
    ax.set_ylabel('Request latency (ms)')
    ax.set_xlabel('Concurrent sandboxes / client threads')

    ax.legend(ncol=5, loc='upper center', bbox_to_anchor=(-.2, 1.2))

    printMyLines("avg latency: ", experiment_lines, lat_avg_holder)
    printMyLines("avg p90: ", experiment_lines, lat_p90_holder)
    printMyLines("avg p99: ", experiment_lines, lat_p99_holder)
    printMyLines("avg p999: ", experiment_lines, lat_p999_holder)





    ax = pl.subplot(gs[1, :]) # row 1, span all columns

    ax.plot( cpu_usage_avg_holder, lat_avg_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax.plot( cpu_usage_avg_holder, lat_p90_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax.plot( cpu_usage_avg_holder, lat_p99_holder, marker=".", markersize=_markersize, label = 'Mean value')
    #ax.plot( cpu_usage_avg_holder, lat_p999_holder, marker=".", markersize=_markersize, label = 'Mean value')
    #ax.plot( cpu_usage_avg_holder, lat_p9999_holder, marker=".", markersize=_markersize, label = 'Mean value')
    #ax.plot( cpu_usage_avg_holder, lat_p99999_holder, marker=".", markersize=_markersize, label = 'Mean value')
    #ax.plot( cpu_usage_avg_holder, lat_p100_holder, marker=".", markersize=_markersize, label = 'Mean value')
    ax.set_ylabel('Request latency (ms)')
    ax.set_xlabel('Mean value of CPU usage (%)')

    pl.title(title, y=-0.4)


    pl.savefig("3-Figs/ratio-" + file_name + "-CS.png", bbox_inches='tight')
    









    
experiment_lines = [1,2,4,8,16,32,64,128,256,512,1024]
experiment_lines = [128]
                                                                                 
makeFig( "dbreader", "HTTP request app", experiment_lines)



