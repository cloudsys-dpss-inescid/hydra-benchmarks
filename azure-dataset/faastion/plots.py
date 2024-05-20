import matplotlib.pyplot as plt
import numpy as np

APPROACHES = ["faastion", "faastlane", "isolate", "process"]
METRICS = ["latency", "footprint"]

workload = 0

def get_axis_values(approach: str, metric: str):
    global workload

    metrics = []
    times = []
    
    with open(f"/tmp/{approach}/{metric}.csv", mode="r") as file:
        lines = file.readlines()
        timestamp = int(lines[0].split(",")[1])

        if workload == 0:
            workload = len(lines)

        for line in lines[:workload]:
            splitted = line.split(",")
            metrics.append(int(splitted[0])/1000) # (us) and (MB)
            times.append((int(splitted[1]) - timestamp)/1000)
    
    # Baseline
    if approach == "faastion":
        workload = len(metrics)

    # Faastlane fails early
    if len(metrics) < workload:
        diff = workload - len(metrics)
        metrics_mean = np.mean(metrics)
        times_mean = times[1] - times[0]
        for _ in range(workload, diff, -1):
            metrics.append(metrics_mean)
            times.append(times[-1] + times_mean)

    return np.array(times), np.array(metrics)


def main():    
    _, axs = plt.subplots(1, 2)

    for index, metric in enumerate(METRICS):
        for approach in APPROACHES:
            x, y = get_axis_values(approach, metric) 
            axs[index].plot(x, y, label=approach)
        axs[index].set_ylabel(metric)
        axs[index].set_xlabel('time')
        axs[index].legend(loc='upper left')
        axs[index].set_title(f'{metric} per time')

    plt.savefig('plots.png')

if __name__ == "__main__":
    main()