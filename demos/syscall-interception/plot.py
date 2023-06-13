import os
import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

class wrk_demo:
    workloads = ["create-shop-carts", "populate-shop-carts", "read-shop-carts"]
    def __init__(self, suite):
        self.bench_avg = []
        self.label = suite
        self.load_log_files(suite)

    def load_log_files(self, suite):
        log_files = list(filter(lambda x: ".log" in x, os.listdir(suite)))
        self.bench_avg = [self.read_log_file(os.path.join(suite, log_file)) for log_file in log_files]
               
    def read_log_file(self, log_file):
        try:
            f = open(log_file, 'r')
            data = f.read().split('\n')
            time_per_request = float(data[5].split()[1][:-2])
            f.close()
            return time_per_request
        except IOError as e:
            print(e)

# deprecated
def plot_ab(log_files):
    data = {os.path.basename(log_file):read_ab_log_file(log_file) for suite in log_files for log_file in suite}
    labels = [label[5:-4] for label in list(data.keys())]
    bench_avg = list(data.values())
    
    plt.rcParams.update({'figure.autolayout': True})
    plt.style.use('ggplot')
    x = [i for i, _ in enumerate(bench_avg)]
    fig = plt.figure()
    plt.tight_layout()
    bars = plt.barh(x, bench_avg, color='green')
    plt.xticks(rotation = 45)
    plt.xlabel("Time (ms)")
    plt.title("Time per Request")
    plt.yticks(x, labels)
    normalized_bench = [i / min(bench_avg) for i in bench_avg]
    for i, v in enumerate(normalized_bench):
        plt.text(bench_avg[i] + 0.04, i, str(round(v,2)), color='blue')
    output = datetime.now().strftime("PLOT_%Y%m%d_%H_%M_%S.jpg")
    plt.savefig(os.path.join("plots", output))

# deprecated
def read_ab_log_file(log_file):
    try:
        f = open(log_file, 'r')
        data = f.read().split('\n')
        time_per_request = float(data[22].split()[3])
        f.close()
        return time_per_request
    except IOError as e:
        print(e)

def plot_wrk(demos):
    barWidth = 0.15
    fig = plt.figure()
    brs = []
    brs.append(list(range(len(wrk_demo.workloads))))
    for i in range(1,len(demos)):
        brs.append([x + barWidth for x in brs[i-1]])
    for i in range(len(demos)):
        plt.bar(brs[i], demos[i].bench_avg, width=barWidth, edgecolor='grey', label=demos[i].label)
    
    plt.xlabel('Workload')
    plt.ylabel('Time (ms)')
    plt.xticks([r + barWidth for r in range(len(wrk_demo.workloads))], wrk_demo.workloads)
    plt.legend()

    output = datetime.now().strftime("PLOT_%Y%m%d_%H_%M_%S.jpg")
    plt.savefig(os.path.join("plots", output))

if __name__ == "__main__":
    def get_wrk_demos(to_search):
        demos = []
        for suite in to_search:
            if os.path.isdir(suite) and not os.path.exists(os.path.join(suite, ".testignore")):
                demos.append(wrk_demo(suite))
        return demos    
    
    # Run 
    to_search = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(os.curdir)
    demos = get_wrk_demos(to_search)
    plot_wrk(demos)