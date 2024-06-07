import matplotlib.pyplot as plt
import numpy as np

#static mpk e dynamic mpk (faastion)
APPROACHES = ["faastion", "isolate", "process", "faastlane"]
WORKLOAD = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

def get_latency_values(approach: str) -> list[float]:
    latencies: list[float] = []
    for requests in WORKLOAD:
        with open(f"/tmp/{approach}/latency-{requests}.log", mode="r") as file:
            line = file.readline()
            latency = float(line.strip().split("ms")[0])
            latencies.append(latency)
    return np.array(latencies)


def get_execution_values(approach: str) -> list[float]:
    executions: list[float] = []
    for requests in WORKLOAD:
        with open(f"/tmp/{approach}/execution-{requests}.log", mode="r") as file:
            lines = file.readlines()
            execution = [float(line.strip())/1000 for line in lines]
            executions.append(np.mean(execution))
    return np.array(executions)

    
def get_footprint_values(approach: str):
    footprints = []
    times = []
    
    with open(f"/tmp/{approach}/footprint-20.csv", mode="r") as file:
        lines = file.readlines()
        timestamp = int(lines[0].split(",")[1])

        for line in lines:
            splitted = line.split(",")
            footprints.append(int(splitted[0])/1000) # (MB)
            times.append((int(splitted[1]) - timestamp)/1000) # (seconds)

    return np.array(times), np.array(footprints)


def get_domain_values(approach: str):
    domains = []
    times = []
    
    with open(f"/tmp/{approach}/domains.csv", mode="r") as file:
        lines = file.readlines()
        timestamp = int(lines[0].split(",")[1])

        for line in lines:
            splitted = line.split(",")
            domains.append(int(splitted[0]))
            times.append((int(splitted[1]) - timestamp)/1_000_000) # (seconds)

    return np.array(times), np.array(domains)

def main():
    _, axs = plt.subplots(2, 2, figsize=(14, 8))

    # Flatten the axs array for easier indexing
    axs = axs.flatten()
    
    x = np.array(WORKLOAD)

    # Latency/#requests graph
    for approach in APPROACHES:
        y = get_latency_values(approach)
        axs[0].plot(x, y, label=approach)
    axs[0].set_ylabel("Client Side Latency (ms)")
    axs[0].set_xlabel("Number of concurrent requests")
    axs[0].legend(loc='upper right')
    axs[0].set_xlim(left=0)
    axs[0].set_ylim(bottom=0)
    axs[0].set_xticks(np.arange(0, max(WORKLOAD) + 1, 2))

    for approach in APPROACHES:
        y = get_execution_values(approach)
        axs[1].plot(x, y, label=approach)
    axs[1].set_ylabel("Server Side Latency (ms)")
    axs[1].set_xlabel("Number of concurrent requests")
    axs[1].legend(loc='upper right')
    axs[1].set_xlim(left=0)
    axs[1].set_ylim(bottom=0)
    axs[1].set_xticks(np.arange(0, max(WORKLOAD) + 1, 2))

    # Domain usage/time graph
    for approach in ["faastion", "faastlane"]:
        x, y = get_domain_values(approach)
        axs[2].plot(x, y, label=approach)
    axs[2].set_ylabel(f"Domain usage for 20 concurrent requests")
    axs[2].set_xlabel("Time (s)")
    axs[2].legend(loc='upper left')
    axs[2].set_xlim(left=0)
    axs[2].set_ylim(bottom=0)

    # Footprint/time graph
    for approach in APPROACHES:
        x, y = get_footprint_values(approach)
        axs[3].plot(x, y, label=approach)
    axs[3].set_ylabel(f"Memory Footprint (MB) for 20 concurrent requests")
    axs[3].set_xlabel("Time (s)")
    axs[3].legend(loc='upper left')
    axs[3].set_xlim(left=0)
    axs[3].set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig('plots.png')

if __name__ == "__main__":
    main()