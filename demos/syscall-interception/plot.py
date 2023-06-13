import os
import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

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

def read_ab_log_file(log_file):
    try:
        f = open(log_file, 'r')
        data = f.read().split('\n')
        time_per_request = float(data[22].split()[3])
        f.close()
        return time_per_request
    except IOError as e:
        print(e)

def plot_wrk(log_files):
    workload = "small"
    log_files = [list(filter(lambda x: os.path.basename(x).find(workload) == 2, suite)) for suite in log_files]
    data = [{os.path.basename(log_file):read_wrk_log_file(log_file) for log_file in suite} for suite in log_files]
    labels = [list(mode.keys())[0][13:-4] for mode in data]

    barWidth = 0.15
    fig = plt.figure()
    brs = []
    brs.append(list(range(3)))
    for i in range(1,len(data)):
        brs.append([x + barWidth for x in brs[i-1]])
    for i in range(len(data)):
        plt.bar(brs[i], data[i].values(), width=barWidth, edgecolor='grey', label=labels[i])
    
    plt.xlabel('Workload')
    plt.ylabel('Time (ms)')
    plt.xticks([r + barWidth for r in range(3)],
        ['create-shop-carts', 'populate-shop-carts', 'read-shop-carts'])
    plt.legend()

    output = datetime.now().strftime("PLOT_%Y%m%d_%H_%M_%S.jpg")
    plt.savefig(os.path.join("plots", output))

def read_wrk_log_file(log_file):
    try:
        f = open(log_file, 'r')
        data = f.read().split('\n')
        time_per_request = float(data[5].split()[1][:-2])
        f.close()
        return time_per_request
    except IOError as e:
        print(e)

if __name__ == "__main__":
    def get_log_files(to_search):
        log_files = []
        for suite in to_search:
            if os.path.isdir(suite) and not os.path.exists(os.path.join(suite, ".testignore")):
                log_files.append([os.path.join(suite, log) for log in list(filter(lambda x: ".log" in x, os.listdir(suite)))])
        return log_files      
    
    # Run 
    to_search = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(os.curdir)
    log_files = get_log_files(to_search)
    plot_wrk(log_files)