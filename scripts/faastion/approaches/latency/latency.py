import matplotlib.pyplot as plt
import numpy as np

APP = "gv_java_native_factors"

def get_mean_time(approach, metric, requests):
    times = []
    
    with open(f"logs/{APP}/{approach}/{metric}-{requests}.log") as file:
        for line in file.readlines():
            if "ms" in line:
                ms = float(line.split("ms")[0])
                times.append(ms)
            else:
                us = float(line.split("us")[0])
                times.append(us/1000) # Change to ms

    return np.mean(times)
    

def main() -> None:
    approaches = ["isolate", "process", "faastion-lazy", "faastlane"]
    metrics = ["latency"]
    workload = [1, 3, 5, 8, 11, 14]

    """
    measures = {
        "isolates": {
            "latency": [***, ***],
        },
        ...
    }
    """
    measures = {}
    for approach in approaches:
        metric_times = {}
        
        for metric in metrics:
            times = [get_mean_time(approach, metric, requests) for requests in workload]
            metric_times[metric] = np.array(times)
        
        measures[approach] = metric_times
       
    x = np.array(workload)
    _, ax = plt.subplots()
    
    for approach, metrics in measures.items():
        for _, times in metrics.items():
            ax.plot(x, times, label=approach)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average Latency (ms)')
    ax.set_xlabel('Number of concurrent requests')
    ax.set_title('Latency for Different Approaches')
    ax.legend(loc='upper left')
    ax.set_ylim(0, 25)

    plt.savefig(f'results/{APP}/Latency.png')

if __name__ == "__main__":
    main()
