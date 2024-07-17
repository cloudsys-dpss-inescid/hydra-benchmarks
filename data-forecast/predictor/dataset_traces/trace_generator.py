#load all the required packages
import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

#for each funciton ID generate a trace for all days and a plot
start_datetime = datetime(2019, 1, 1, 0, 0, 0)
dataset_file_name = "invocations_per_function_md.anon.d"

#Create a file with all the hash functions IDs
def generate_trace_ids_file(dataset_dir, all_traces_ids_file):

  traces_ids = set()

  for i in range(1, 15):

      file_number = str(i).zfill(2)  #transform 1 in 01

      with open(dataset_dir + dataset_file_name + file_number + ".csv" , 'r') as file:
        for line in file:
          if 'HashOwner' in line: #ignore first line
              next

          function_id = line.split(',')[2]
          traces_ids.add( function_id )
          #print(function_id)

  with open(all_traces_ids_file, 'w') as file:
    for trace_id in traces_ids:
      file.write(trace_id + '\n')


  print("generate_trace_ids_file - done")


def get_function_traces_from_file(file_number, trace_id, dataset_dir):
  file_number = str(file_number).zfill(2)  #transform 1 in 01

  with open(dataset_dir + dataset_file_name + file_number + ".csv" , 'r') as file:
    for line in file:
      if trace_id in line:
        calls_array = line.split(',')[4:]
        return calls_array

    return ['0'] * 1440 #if is not found on the dataset return zero values for each timestamp

def generate_and_plot_trace_id(trace_id, dataset_dir, result_dir):

    timestamps_array = []
    calls_array = []
    for i in range(1, 15):
      calls_array = calls_array + get_function_traces_from_file(i, trace_id, dataset_dir)


    # Open file to write the trace data
    output_file_name = result_dir + "traces_datapoints/" + trace_id + ".csv"
    with open(output_file_name, 'w') as output_file:
      output_file.write("item_id,timestamp,target\n")

      # Write each entry from calls_array to the output file
      for index, value in enumerate(calls_array):
          current_datetime = start_datetime + timedelta(minutes=index)

          timestamps_array = timestamps_array + [current_datetime]
          output_file.write(f"{trace_id},{current_datetime.strftime('%Y-%m-%d %H:%M:%S') },{value}\n")
    
    if False:
      plt.figure(figsize=(40, 6))
      calls_array_int = [int(value) for value in calls_array]

      plt.plot(timestamps_array, calls_array_int, color="blue", label="data points")
      plt.legend()

      plt.savefig(result_dir + "traces_plots/" + trace_id + ".png", bbox_inches='tight')
      plt.close()  # Close the plot without displaying it

## this will generate the traces and plots for all the trace_ids in the dataset, that have not yet been generated
def generate_all_traces(dataset_dir, result_dir, all_traces_ids_files_name):

  # List files in the directory
  completed_traces = os.listdir(result_dir + "traces_plots/")
  print("# completed_traces: " + str( len(completed_traces)))

  with open(all_traces_ids_files_name , 'r') as file:
    for trace_id in file:
      trace_id = trace_id.strip()  # Remove any trailing newline characters

      if trace_id + ".csv" in  completed_traces :
        #print("skiping on " + trace_id)
        continue

      print("working on " + trace_id)
      generate_and_plot_trace_id(trace_id, dataset_dir, result_dir)

#dir_path = None
def read_csv_trace(trace_id, dataset_dir, trace_dir_drive):
    #global trace_path
    
    trace_path = os.path.join(trace_dir_drive, "traces_datapoints/", trace_id + '.csv')
    
    #if trace_path is None;  
       #dir_path = Path("/path/to/file")
    
    # case the trace has not yet being generated
    if not os.path.isfile(trace_path):
        generate_and_plot_trace_id(trace_id, dataset_dir, trace_dir_drive)
    
    points = pd.read_csv(trace_path)
    
    return points








