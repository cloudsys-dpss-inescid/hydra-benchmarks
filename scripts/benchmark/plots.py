import re
import matplotlib.pyplot as plt
import numpy as np
import argparse

def read_file(file_path, mean_attempts):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return [float(lines[i].split()[3]) for i in range(0, mean_attempts*2, 2)]
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []


def apache_benchmark_logs(args):
    file_path = "/tmp/ab-{run}.log"
    means = []

    for run in range(1, args.workload + 1):
        values = read_file(file_path.format(run=run), args.mean_attempts)
        if values:
            means.append(np.mean(values))

    plt.plot(range(1, len(means) + 1), means)
    plt.ylabel("Time of Execution (ms)")
    plt.xlabel("No. of Invocations")
    plt.title("Execution using Memory Isolation")
    plt.show()
    plt.savefig('memisolation.png')


def lambda_logs(args):
    def get_times(lines, start_index, step):
        return [float(re.search(pattern, lines[i]).group()) for i in range(start_index, len(lines) - 1, step)]

    def calc_percentage(mean_time, total_time):
        return (mean_time * 100) / total_time

    def print_stats(title, mean_time, total_time):
        print(f"\t{title} mean time:")
        print(f"\t\t{round(mean_time, 4)} ms")
        print(f"\t\t{round(calc_percentage(mean_time, total_time), 4)} % (total execution)\n")

    file_template = "/tmp/lambda-{run}.log"
    pattern = r'\d+\.\d+'
    init_times = []
    load_times = []
    first_domain_times = []
    first_filter_times = []

    domain_times = []
    filter_times = []

    for run in range(1, args.mean_attempts + 1):
        with open(file_template.format(run=run), "r") as file:
            lines = file.readlines()
            init_times.append(float(re.search(pattern, lines[0]).group()))
            load_times.append(float(re.search(pattern, lines[1]).group()))
            first_domain_times.append(float(re.search(pattern, lines[2]).group()))
            first_filter_times.append(float(re.search(pattern, lines[3]).group()))
            domain_times.extend(get_times(lines, 4, 2))
            filter_times.extend(get_times(lines, 5, 2))
    
    all_domain_times = domain_times + first_domain_times
    all_filter_times = filter_times + first_filter_times

    # First runs mean
    init_mean = np.mean(init_times)/1000
    load_mean = np.mean(load_times)/1000
    first_domain_mean = np.mean(first_domain_times)/1000
    first_filter_mean = np.mean(first_filter_times)/1000

    # Second to last runs mean
    domain_mean = np.mean(domain_times)/1000
    filter_mean = np.mean(filter_times)/1000
    
    # All runs mean
    all_domain_mean = np.mean(all_domain_times)/1000
    all_filter_mean = np.mean(all_filter_times)/1000

    first_mean_time = read_file("/tmp/ab-1.log", args.mean_attempts)
    total_means = first_mean_time + []
    first_run_mean_total_time = np.mean(first_mean_time)

    file_template = "/tmp/ab-{run}.log"
    means = []

    for run in range(2, args.workload + 1):
        values = read_file(file_template.format(run=run), args.mean_attempts)
        if values:
            means.append(np.mean(values))
    
    total_means += means
    second_last_mean_time = np.mean(means)

    total_mean_time = np.mean(total_means)

    print(f"First run mean total time: {round(first_run_mean_total_time, 4)} ms")
    print_stats("Init", init_mean, first_run_mean_total_time)
    print_stats("Load", load_mean, first_run_mean_total_time)
    print_stats("Domain acquisition", first_domain_mean, first_run_mean_total_time)
    print_stats("Apply filter", first_filter_mean, first_run_mean_total_time)

    print(f"Second to last mean total time: {round(second_last_mean_time, 4)} ms")
    print_stats("Domain acquisition", domain_mean, second_last_mean_time)
    print_stats("Apply filter", filter_mean, second_last_mean_time)

    print(f"Total execution mean time: {round(total_mean_time, 4)} ms")
    print_stats("Domain acquisition", all_domain_mean, total_mean_time)
    print_stats("Apply filter", all_filter_mean, total_mean_time)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workload", type=int, default=50)
    parser.add_argument("-m", "--mean-attempts", type=int, default=10)
    parser.add_argument("-t", "--type", choices=["ab", "lambda"], default="ab")
    args = parser.parse_args()

    match(args.type):
        case "ab":
            apache_benchmark_logs(args)
        case "lambda":
            lambda_logs(args)
    
    

if __name__ == "__main__":
    main()
