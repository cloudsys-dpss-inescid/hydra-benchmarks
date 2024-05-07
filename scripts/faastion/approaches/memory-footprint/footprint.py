import matplotlib.pyplot as plt
import numpy as np

APP = "gv_java_native_factors"

def get_mean_mem(approach, requests):
    mem = []
    
    for run in range(1, 51):
        with open(f"results/{APP}/{approach}/lambda-{requests}-{run}.rss") as file:
            lines = file.readlines()
            if len(lines) == 1:
                continue
            for line in lines:
                number = int(line)
                if number == 0:
                    continue
                mem.append(number/1000) #MB

    return np.mean(mem)
    

def main() -> None:
    approaches = ["isolate", "process", "faastion-lazy", "faastlane"]
    workload = [1, 3, 5, 8, 11, 14]

    """
    measures = {
        "isolates": [***, ***],
        ...
    }
    """
    measures = {}
    for approach in approaches:
        mem = [] 
        for requests in workload:
            mem.append(get_mean_mem(approach, requests))
        measures[approach] = np.array(mem)
       
    x = np.array(workload)
    _, ax = plt.subplots()
    
    for approach, mem in measures.items():
        ax.plot(x, mem, label=approach)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average Memory Footprint (MB)')
    ax.set_xlabel('Number of concurrent requests')
    ax.set_title('Memory Footprint for Different Approaches')
    ax.legend(loc='upper left')
    ax.set_ylim(0, 250)

    plt.savefig(f'results/{APP}/Memory.png')

if __name__ == "__main__":
    main()
