import os
import sys
import pathlib
from datetime import datetime
import matplotlib.pyplot as plt

def plot(log_files):
    print("processing log files")
    data = {os.path.basename(log_file):read_log_file(log_file) for log_file in log_files}
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

def read_log_file(log_file):
    try:
        f = open(log_file, 'r')
        data = f.read().split('\n')
        time_per_request = float(data[22].split()[3])
        f.close()
        return time_per_request
    except IOError as e:
        print(e)

if __name__ == "__main__":
    def get_log_files(to_search):
        log_files = []
        for suite in to_search:
            if os.path.isdir(suite):
                log_files += [os.path.join(suite, log) for log in list(filter(lambda x: ".log" in x, os.listdir(suite)))]
        return log_files      
    
    # Run 
    to_search = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(os.curdir)
    log_files = get_log_files(to_search)
    plot(log_files)