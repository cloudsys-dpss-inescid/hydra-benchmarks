import matplotlib.pyplot as plt
import numpy as np

#static mpk e dynamic mpk (faastion)
APPROACHES = ["faastion", "isolate", "process", "faastlane"]
WORKLOAD = [1, 2, 4, 8, 12, 16, 20]

def get_latency_values(approach: str) -> list[float]:
    latencies: list[float] = []
    for requests in WORKLOAD:
        with open(f"/tmp/{approach}/latency-{requests}.log", mode="r") as file:
            line = file.readline()
            latency = float(line.strip())

            if "ms" in latency:
                latencies.append(latency*1000) #(us)
            else:
                latencies.append(latency)
    return np.array(latencies)

    
def get_footprint_values(approach: str, requests: int):
    footprints = []
    times = []
    
    with open(f"/tmp/{approach}/footprint-{requests}.csv", mode="r") as file:
        lines = file.readlines()
        timestamp = int(lines[0].split(",")[1])

        for line in lines:
            splitted = line.split(",")
            footprints.append(int(splitted[0])/1000) # (MB)
            times.append((int(splitted[1]) - timestamp)/1000) # (seconds)

    return np.array(times), np.array(footprints)


def main():
    _, axs = plt.subplots(2, 2, figsize=(14, 8))

    # Flatten the axs array for easier indexing
    axs = axs.flatten()
    
    x = np.array(WORKLOAD)

    # Latency/#requests graph
    for approach in APPROACHES:
        y = get_latency_values(approach)
        axs[0].plot(x, y, label=approach)
    axs[0].set_ylabel("Average Latency (us)")
    axs[0].set_xlabel("Number of concurrent requests")
    axs[0].legend(loc='upper right')

    # Footprint/time graph
    for index, requests in enumerate(WORKLOAD[3:]):
        current_plot = index + 1
        for approach in APPROACHES:
            x, y = get_footprint_values(approach, requests)
            axs[current_plot].plot(x, y, label=approach)

        axs[current_plot].set_ylabel(f"Memory Footprint for {requests} concurrent requests (MB)")
        axs[current_plot].set_xlabel("Time (s)")
        axs[current_plot].legend(loc='upper left')

    plt.tight_layout()
    plt.savefig('plots.png')

if __name__ == "__main__":
    main()