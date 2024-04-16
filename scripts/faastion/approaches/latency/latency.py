import matplotlib.pyplot as plt
import numpy as np


def get_mean_time(approach, metric, requests):
    times = []
    
    with open(f"logs/{approach}/{metric}-{requests}.log") as file:
        for line in file.readlines():
            if "ms" in line:
                ms = float(line.split("ms")[0])
                times.append(ms*1000) # Change to us
            else:
                us = float(line.split("us")[0])
                times.append(us)

    return np.mean(times)
    

def main() -> None:
    approaches = ["isolate", "process", "faastion-eager", "faastion-lazy"]
    metrics = ["latency"]
    workload = [1, 3, 5, 8, 11, 14]

    """
    measures = {
        "isolates": {
            "latency": [***, ***],
            "connect": [***, ***],
            "TTFB": [***, ***],
            "TTLB": [***, ***],
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
    

    x = np.arange(len(workload))
    width = 0.15
    multiplier = 0

    _, ax = plt.subplots(layout='constrained')

    for approach, metrics in measures.items():
        bottom = np.zeros(len(workload))
        offset = width * multiplier
        for metric, times in metrics.items():
            ax.bar(x + offset, times, width, label=approach, bottom=bottom)
            bottom += times
        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Latency (us)')
    ax.set_xlabel('Number of requests')
    ax.set_title('Latency for Different Approaches')
    ax.set_xticks(x + width, workload)
    ax.legend(loc='upper left', ncols=len(approaches))
    ax.set_ylim(0, 700)

    plt.savefig(f'results/Latency.png')


if __name__ == "__main__":
    main()
