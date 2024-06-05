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



def read_cpu_usage(path, experience_start_time = 0):

    cpu_points = {"avg":[],"0":[]}
    counter = 0
    us_value_sum = 0
    sys_value_sum = 0
    idle_value_sum = 0
    io_value_sum = 0

    try:
        with open(path + '/lambda.cpu') as file:
            for line in file:

                if "timestamp" in line:
                    
                    if counter > 0:
                        cpu_points["avg"].append( [ timestamp, us_value_sum/counter, sys_value_sum/counter, idle_value_sum/counter, io_value_sum/counter ] )
                        counter = 0
                        us_value_sum = 0
                        sys_value_sum = 0
                        idle_value_sum = 0
                        io_value_sum = 0
                    
                    timestamp = float(line.split(":")[1]) - experience_start_time
                else:
                    data_splited = line.split(":")

                    points_key = data_splited[0].strip("%").strip()
                    us_value = float( data_splited[1].split(",")[0].split()[0] )
                    sys_value=  float( data_splited[1].split(",")[1].split()[0] )
                    idle_value= float( data_splited[1].split(",")[3].split()[0] )
                    io_value= float( data_splited[1].split(",")[4].split()[0] )

                    us_value_sum += us_value
                    sys_value_sum += sys_value
                    idle_value_sum += idle_value
                    io_value_sum += io_value
                    counter += 1
                                        
                    if( not cpu_points.get(points_key) ):
                        cpu_points[points_key] = []

                    cpu_points[points_key].append( [ timestamp, us_value, sys_value, idle_value, io_value ] )

    except Exception as e:
        print("Error processing " + path + ":")
        raise e
    return cpu_points


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

def process_log_first_line(line):    
    right_side = line.split("[")

    since_reference = right_side[1].split("]")[0]
    from_boot_to_reference = right_side[2].split("]")[0]

    return float(since_reference), float(from_boot_to_reference)


def get_GC_G1_datapoints(file_path, experience_start_time = 0):

    lambda_file = file_path + "/lambda.log"
    
    Pause_Young = []
    Pause_duration = []
    Isolate_GCs = []    
    Incremental_GC = []
    Full_GC = []    
    number_of_reading_erros = 0

    try:
        with open(lambda_file ) as file:
            since_reference, from_boot_to_reference = process_log_first_line(file.readline()) #to skip first line
            for line in file:

                if "Pause Young" in line:
                    timestamp_string =  (line.split("]")[0]).split("[")[1]
                    value_miliseconds = float(timestamp_string[:-1]) * 1000
                    Pause_Young.append( since_reference + value_miliseconds - experience_start_time)

                    gc_duration_string = float( (line.split()[-1]).split("ms")[0] )
                    Pause_duration.append(gc_duration_string)
                
                elif "GC: before" in line and "[[" in line:
                    try:
                        timestamp_nanoseconds =  float( ( line.split("[[")[1] ).split(" GC: before")[0] )
                        timestamp_miliseconds = timestamp_nanoseconds/1000000
                        timestamp_ajusted = since_reference + timestamp_miliseconds - from_boot_to_reference
                        Isolate_GCs.append(timestamp_ajusted - experience_start_time)
                    except Exception as e:
                        #print("Error line: " + line)
                        number_of_reading_erros += 1
                
                #This is for the normal GC events 
                elif "Incremental GC" in line:
                    timestamp_string =  float( (line.split()[0]).split("[")[1] )
                    Incremental_GC.append( since_reference + timestamp_string - experience_start_time )
                
                elif "Full GC" in line:
                    timestamp_string =  float( (line.split()[0]).split("[")[1] )
                    Full_GC.append( since_reference + timestamp_string - experience_start_time )
                    

    except Exception as e:
        print("Error processing " + lambda_file + " and line: " + line)
        raise e
    
    return Pause_Young, Pause_duration, Isolate_GCs, number_of_reading_erros, Incremental_GC, Full_GC

def get_starting_time(file_path):
    
    lambda_file = file_path + "/lambda.log"

    try:
        with open(lambda_file ) as file:
            since_reference, from_boot_to_reference = process_log_first_line(file.readline()) #to skip first line
        
    except Exception as e:
        print("Error processing " + lambda_file + ":")
        raise e
    
    return since_reference, from_boot_to_reference


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


    idle_timestamp, idle_wait, idle_delay, idle_run = results.get_timehist_datapoints(file_path,"idle")

def get_timehist_datapoints(file_path, task, experience_start_time = 0):

    thread_file = file_path + "/perf_timehist.log"
    #data_points = read_CClient_latency_lines(thread_file)
    timestamp_array = []
    wait_time = []
    sch_delay = []
    run_time = []

    try:
        with open(thread_file) as file:
            first_line = file.readline() #to skip the first three lines
            first_line = file.readline() 
            first_line = file.readline() 
            benchmark_init = float(file.readline().split()[0])*1000 
            for line in file:

                if task in line:
                    timestamp = float(line.split()[0])*1000
                    wait = float(line.split()[-3])
                    delay = float(line.split()[-2])
                    run = float(line.split()[-1])

                    timestamp_array.append(timestamp - experience_start_time - benchmark_init)
                    wait_time.append(wait)
                    sch_delay.append(delay)
                    run_time.append(run)

    except Exception as e:
        print("Error processing " + thread_file + ":")
        raise e
    
    return timestamp_array, wait_time, sch_delay, run_time


def get_latency_datapoints(file_path, thread_id, experience_start_time = 0):

    thread_file = file_path + "/latency_thread" + str(thread_id) + ".log"
    #data_points = read_CClient_latency_lines(thread_file)
    timestamp_array = []
    latency_array = []

    try:
        with open(thread_file) as file:
            first_line = file.readline() #to skip first line
            for line in file:
                timestamp_array.append( float(line.split(",")[0]) - experience_start_time)
                latency_array.append( float(line.split(",")[1]) )
    except Exception as e:
        print("Error processing " + thread_file + ":")
        raise e
    
    return timestamp_array, latency_array


def get_latency_sleep_datapoints(file_path, experience_start_time = 0):
    sleep_duration_array = []
    process_time_array = []
    timestamp_array = []
    duration_at_client_array = []
    try:
        with open(file_path) as file:
            for line in file:
                if "process time (us)" in line:
                    if "sleep duration (nanoseconds)" in line:
                        sleep_duration = float( line.split('sleep duration (nanoseconds)')[1].split(",")[0].replace('}"', '').split(":")[1] ) / 1000000
                        sleep_duration_array.append(sleep_duration)
                    process_time = float( line.split('process time (us)":')[1].split("}")[0] ) / 1000
                    process_time_array.append(process_time)
                elif "timestamp" in line:
                    timestamp = float( line.split("timestamp")[1].split(",")[0] )  - experience_start_time
                    duration_at_client = float( line.split("duration")[1].split(")")[0] )
                    timestamp_array.append(timestamp)
                    duration_at_client_array.append(duration_at_client)
    except Exception as e:
        print("Error processing " + file_path + " line :" + line )
        raise e
    
    return sleep_duration_array, process_time_array, timestamp_array, duration_at_client_array

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
    try:
        command = "perf script -F time,event > context_switches.txt"
        subprocess.run(command, shell=True, check=True, cwd=file_path)
    except Exception as e:
        print("Error processing  perf" + e + ":")
                

def get_context_switches_datapoints(file_path, experience_start_time = 0):

    context_switches_file = file_path + "/context_switches.txt"
    lambda_file = file_path + "/lambda.log"

    context_switches_timestamps = []

    try:

        with open(lambda_file ) as file:
            benchmark_init, _ = process_log_first_line(file.readline()) #get timestamp when benchmark started. This is a relative time from 2020 that I use in all values, is deifined in shared.sh

        
        first_timestamp = -1
        with open(context_switches_file ) as file:
            #first_timestamp = float(file.readline()) #to skip first line

            for line in file:

                #This only works for perf sched record 
                timestamp_value = float( (line.split("]")[1]).split(":")[0] ) * 1000 #from seconds to miliseconds
                #This qorks for perf record -e context-switches
                #timestamp_value = float( line.split(":")[0] ) * 1000 #from seconds to miliseconds

                if( first_timestamp < 0): #get first timestamp
                    first_timestamp = timestamp_value

                timestamp_relative = timestamp_value - first_timestamp + benchmark_init 
                
                context_switches_timestamps.append( timestamp_relative - experience_start_time)

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
