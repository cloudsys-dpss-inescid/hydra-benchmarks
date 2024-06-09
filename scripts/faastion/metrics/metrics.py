import matplotlib.pyplot as plt
import numpy as np

APPROACHES = ["faastion", "isolate", "process", "faastlane"]
#BENCHMARKS = ["factors", "matmul", "filehashing", "httprequest", "sleep", "nativehw"]
BENCHMARKS = ["factors", "matmul", "httprequest", "nativehw", "sleep"]

def get_latency_values():
    approaches_latencies = {}

    for approach in APPROACHES:
        latencies = []
        
        for benchmark in BENCHMARKS:
            with open(f"/tmp/{approach}/{benchmark}-latency.log", mode="r") as file:
                lines = file.readlines()
                benchmark_latencies = [float(line.strip()) for line in lines]
                avg_latency = np.mean(benchmark_latencies)
                latencies.append(avg_latency)
    
        approaches_latencies[approach] = np.array(latencies)

    return approaches_latencies


def get_footprint_values(approach: str):
    footprints = []
    times = []
    
    with open(f"/tmp/{approach}/footprint.csv", mode="r") as file:
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


# LATENCY
approaches_latencies = get_latency_values()

x = np.arange(len(BENCHMARKS))  # the label locations
width = 0.2  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for approach, measurement in approaches_latencies.items():
    offset = width * multiplier
    ax.bar(x + offset, measurement, width, label=approach)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Server Side Latency (us)')
ax.set_title('Average latency per approach')
ax.set_xticks(x + width, BENCHMARKS)
ax.legend(loc='upper left', ncols=4)
ax.set_ylim(bottom=0)

plt.savefig('latency.png')

# FOOTPRINT
fig, ax = plt.subplots(layout='constrained')

for approach in APPROACHES:
    x, y = get_footprint_values(approach)
    ax.plot(x, y, label=approach)
ax.set_ylabel(f"Memory Footprint (MB)")
ax.set_xlabel("Time (s)")
ax.legend(loc='upper left')
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

plt.savefig('footprint.png')

# Domain usage/time graph
fig, ax = plt.subplots(layout='constrained')

for approach in ["faastion", "faastlane"]:
    x, y = get_domain_values(approach)
    ax.plot(x, y, label=approach)
ax.set_ylabel(f"Domain usage for 20 concurrent requests")
ax.set_xlabel("Time (s)")
ax.legend(loc='upper left')
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

plt.savefig('domains.png')
