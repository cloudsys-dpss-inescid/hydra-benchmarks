#!/usr/bin/python

import os
import numpy as np
import subprocess
import os

def read_benchmark_throughput(path):
    tput = []
    try:
        with open(path + '/ab.log') as file:
            for line in file:
                if 'Requests per second:' in line:
                    tput.append(float(line.split()[3]))
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return tput

def read_benchmark_memory(path):
    mem = []
    try:
        mem = []
        with open(path + '/lambda.rss') as file:
            for line in file:
                mem.append(int(line))
        if len(mem) < 7:
            print("Warning, not enough memory data points from {path}".format(path=path))
        # Use the last 5 samples before the last one.
        mem = mem[-6:-1]
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return mem

def read_std_latency(path):
    lstd = []
    try:
        with open(path + '/ab.log') as file:
            for line in file:
                if '%' in line:
                    lstd.append(float(line.split()[1]))
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return lstd



def read_cpu_usage(path):
    lstd = []
    try:
        with open(path + '/lambda.cpu') as file:
            for line in file:
                timestamp = float(line.split(",")[0])
                us_value = float(  ((line.split(",")[1]).split(":")[1]).split()[0]    )
                sys_value= float(  (line.split(",")[2]).split()[0]    )
                idle_value= float(  (line.split(",")[4]).split()[0]    )

                lstd.append( [ timestamp, us_value, sys_value, idle_value ] )
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return lstd


def read_tpr_latency(path):
    tpr = []
    try:
        with open(path + '/ab.log') as file:
            for line in file:
                if 'Time per request:' in line:
                    tpr.append(float(line.split()[3]))
                    break
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return tpr


def read_tpr_raw_latency(path):
    tpr_raw = []
    try:
        with open(path + '/raw-data-points.tsv') as file:
            first_line = file.readline() #to skip first line
            for line in file:
                tpr_raw.append([ float(line.split()[6]), float(line.split()[7]), float(line.split()[8]), float(line.split()[9]) ] )
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return tpr_raw


def read_latency_lines(path):
    tpr_raw = []
    try:
        with open(path ) as file:
            first_line = file.readline() #to skip first line
            for line in file:
                tpr_raw.append(float(line))
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return tpr_raw


def read_CClient_latency_lines(path):
    tpr_raw = []
    try:
        with open(path ) as file:
            first_line = file.readline() #to skip first line
            for line in file:
                tpr_raw.append( [ float(line.split(",")[0]), float(line.split(",")[1]) ] )
    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return tpr_raw


def getExperimentLatency(isolate_lat_tpr_raw):
    requestLatency = []

    for e in isolate_lat_tpr_raw:
        requestLatency.append(e[1])

    return requestLatency

def processCpuUsage(isolate_cpu_usage):
    cpuUsage = []
    cpuReadingTimestamp = []

    for e in isolate_cpu_usage:
        cpuUsage.append(100 - e[3])
        cpuReadingTimestamp.append(e[0])

    return [cpuReadingTimestamp, cpuUsage]


def arrays_split(input_array):
    """
    Recebe um array de arrays, onde cada sub-array contém duas entradas.
    Retorna dois arrays, um com todas as primeiras entradas e outro com todas as segundas entradas.
    """
    first_array = [sub_array[0] for sub_array in input_array]
    second_array = [sub_array[1] for sub_array in input_array]
    
    return first_array, second_array


def get_GC_G1_datapoints(file_path):

    lambda_file = file_path + "/lambda.log"
    
    Pause_Young = []
    Pause_duration = []


    try:
        with open(lambda_file ) as file:
            first_timestamp = float(file.readline()) #to skip first line
            for line in file:

                if "Pause Young" in line:
                    timestamp_string =  (line.split("]")[0]).split("[")[1]
                    value_miliseconds = float(timestamp_string[:-1]) * 1000
                    Pause_Young.append( first_timestamp + value_miliseconds)

                    gc_duration_string = float( (line.split()[-1]).split("ms")[0] )
                    Pause_duration.append(gc_duration_string)

    except Exception as e:
        print("Error processing " + lambda_file + ":")
        raise e
    
    return Pause_Young, Pause_duration



def get_GC_datapoints(file_path):

    lambda_file = file_path + "/lambda.log"
    
    Incremental_GC = []
    Full_GC = []

    try:
        with open(lambda_file ) as file:
            first_timestamp = float(file.readline()) #to skip first line
            for line in file:

                if "Incremental GC" in line:
                    Incremental_GC.append( first_timestamp + float( (line.split()[0]).split("[")[1] ) )
                elif "Full GC" in line:
                    Full_GC.append( first_timestamp + float( (line.split()[0]).split("[")[1] ) )

    except Exception as e:
        print("Error processing " + lambda_file + ":")
        raise e
    
    return Incremental_GC, Full_GC



def get_latency_datapoints(file_path, thread_id):

    thread_file = file_path + "/latencias_thread" + str(thread_id) + ".log"
    data_points = read_CClient_latency_lines(thread_file)
    timestamp_array, latency_array = arrays_split(data_points)
    
    return timestamp_array, latency_array

def get_thread_throughput(timestamp_left, timestamp_rigth, timestamp_array):

    total_below = ( np.array(timestamp_array) < timestamp_left).sum()
    total_larger = ( np.array(timestamp_array) > timestamp_rigth).sum()

    total_count = len(timestamp_array) - total_below - total_larger
    elipsed_time_ms = timestamp_rigth - timestamp_left
    elipsed_time_s = elipsed_time_ms/1000 #miliseconds to seconds
    throughput = total_count/elipsed_time_s

    return throughput



def process_perf_sched_data(file_path):

    command = "perf script | grep sched_switch > context_switches.txt"
    subprocess.run(command, shell=True, check=True, cwd=file_path)

def process_perf_record_data(file_path):

    command = "perf script -F time,event > context_switches.txt"
    subprocess.run(command, shell=True, check=True, cwd=file_path)

def get_context_switches_datapoints(file_path):

    context_switches_file = file_path + "/context_switches.txt"
    lambda_file = file_path + "/lambda.log"

    context_switches_timestamps = []

    try:

        with open(lambda_file ) as file:
            benchmark_init = float(file.readline()) #get timestamp when benchmark started. This is a relative time from 2020 that I use in all values, is deifined in shared.sh
            
        
        first_timestamp = -1
        with open(context_switches_file ) as file:
            #first_timestamp = float(file.readline()) #to skip first line

            for line in file:

                #This only works for perf sched record 
                #timestamp_value = float( (line.split("]")[1]).split(":")[0] ) * 1000 #from seconds to miliseconds
                #This qorks for perf record -e context-switches
                timestamp_value = float( line.split(":")[0] ) * 1000 #from seconds to miliseconds

                if( first_timestamp < 0): #get first timestamp
                    first_timestamp = timestamp_value

                timestamp_relative = timestamp_value - first_timestamp + benchmark_init 
                
                context_switches_timestamps.append( timestamp_relative )

    except Exception as e:
        print("Error processing " + lambda_file + ":")
        raise e
    
    return context_switches_timestamps





def process_result(path):
    # Throughput (ops/s) of each iteration.
    tput = []
    # Memory samples (rss in kbs) of each iteration.
    mem = []
    # Latency standard deviation  (50% 66% 75% 80% 90% 95% 98% 99% 100% ms) of each iteration.
    lstd = []
    # Time per request  [ms] (mean)
    tpr = []
    # Time per request  [ms] (all points raw)
    tpr_raw = []    

    # Cpu usage  [%]    % user,  % system,  % idle
    cusage = []

    for file in os.scandir('../results/' + path): # TODO - check how this would work.
        if file.is_dir():
            #mem.extend(read_benchmark_memory(file.path))
            tput.extend(read_benchmark_throughput(file.path))
            lstd.extend(read_std_latency(file.path))
            tpr.extend(read_tpr_latency(file.path))
            tpr_raw.extend(read_tpr_raw_latency(file.path))
            cusage.extend(read_cpu_usage(file.path))


    # Convert to numpy arrays (help with mean and std).
    tput = np.array(tput)
    #mem = np.array(mem)

    # Convertion from kbs to mbs and to gbs.
    #mem = mem / 1024 / 1024

    # Numpy array with the efficiency (ops/s/GB) samples.
    #eff = tput / mem.mean()
    results = {}
    results["tput_avg"] = round(tput.mean(), 3)
    results["tput_std"] = round(tput.std(), 3)
    #results["mem_avg"] = round(mem.mean(), 3)
    #results["mem_std"] = round(mem.std(), 3)
    #results["eff_avg"] = round(eff.mean(), 3)
    #results["eff_std"] = round(eff.std(), 3)
    results["lan_std"] = lstd
    results["lat_tpr"] = tpr
    results["lat_tpr_raw"] = tpr_raw
    results["cpu_usage"] = cusage

    #print("{path} {results}".format(path=path, results=results))
    return results
