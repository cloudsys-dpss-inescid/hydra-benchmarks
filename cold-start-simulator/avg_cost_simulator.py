import matplotlib.pyplot as plt
import matplotlib as mpl

plot_precision = 1

files_path = "/home/claudiocorreia/work/hydra/benchmarks/azure-dataset/input/" #dataset location
files_names = ["function_durations_percentiles.anon.d01.csv",
               "function_durations_percentiles.anon.d02.csv",
               "function_durations_percentiles.anon.d03.csv",
               "function_durations_percentiles.anon.d04.csv",
               "function_durations_percentiles.anon.d05.csv",
               "function_durations_percentiles.anon.d06.csv",
               "function_durations_percentiles.anon.d07.csv",
               "function_durations_percentiles.anon.d08.csv",
               "function_durations_percentiles.anon.d09.csv",
               "function_durations_percentiles.anon.d10.csv",
               "function_durations_percentiles.anon.d11.csv",
               "function_durations_percentiles.anon.d12.csv",
               "function_durations_percentiles.anon.d13.csv",
               "function_durations_percentiles.anon.d14.csv"]
def plot_cost(cold_start_duration):

    dic_counter = {} # key is the percentage cost of the cold start for the functions, and the value the number of function that suffered this cost
    number_of_ignored_function = 0
    global_function_e2e = 0 # E2E, end two end execution duration

    for file_name in files_names:

        with open(files_path + file_name) as f:
            next(f) #skip first line
            
            for line in f:
                line = line.split(",")
                curr_avg = float(line[3]) #ms there some values at zero
                curr_count = float(line[4])
                
                if curr_avg <= 0:
                    number_of_ignored_function += curr_count
                    curr_avg = 0.9
                    #continue

                percentage_cost = round((100*cold_start_duration)/(curr_avg + cold_start_duration), plot_precision) #I am adding the cold_start_duration so that E2E = cold_start_duration + execution_duration

                if percentage_cost not in dic_counter:
                    dic_counter[percentage_cost] = 0
                    
                dic_counter[percentage_cost] += curr_count

                global_function_e2e += (curr_avg + cold_start_duration)*curr_count

    #plot the CDF
    dic_counter = dict(sorted(dic_counter.items()))

    global_function_number = sum(dic_counter.values())
    global_cold_duration = global_function_number*cold_start_duration
    percentage_of_cold_time = round((100*global_cold_duration)/global_function_e2e,2)

    total_sum = 0
    for k in dic_counter:
        total_sum += dic_counter[k]
        percentual_sum = (100*total_sum)/global_function_number
        dic_counter[k] = percentual_sum

    avg_function_duration = round(global_function_e2e / global_function_number, 2)
    print(f"Avg function duration {avg_function_duration} ms. There where a total of {number_of_ignored_function} function calls that had 0ms duration, and I have relpaced with 0.9ms, this happened in a total of {number_of_ignored_function + global_function_number} function calls, corresponding to { round((number_of_ignored_function*100)/(number_of_ignored_function + global_function_number),3)}%,")

    x = dic_counter.keys()
    y = dic_counter.values()
    plt.scatter(x, y)
    plt.step(x, y, where='post', label=f"{cold_start_duration}ms cold start, represents {percentage_of_cold_time}% of the total execution time") 


mpl.rcParams["font.size"] = 20

plt.figure(figsize=(15, 8))

plot_cost(1)
plot_cost(5)
plot_cost(10)
plot_cost(20)

plt.axvline(x = 100, color = 'r', label = '100% cost (impossible, only if execution_duration=0)')

plt.legend()
plt.legend(loc="lower right")
plt.grid()
plt.title("Latency impact of cold starts based on Azure dataset *Averages*")
plt.xlabel("Percentage of the cold start relative to the function End two End (E2E) time (%)\n E2E time = cold_start_duration + execution_duration.")
plt.ylabel("CDF of the number of invocations (%)")
plt.tight_layout()
plt.savefig("cold_start_cost.png")



