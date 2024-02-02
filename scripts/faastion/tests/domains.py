import argparse
import matplotlib.pyplot as plt
import numpy as np

PATH_TEMPLATE = 'logs/{approach}-{n}-{run}.log'

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--ndomains", type=int, required=True)
parser.add_argument("-w", "--workload", type=int, required=True)
parser.add_argument(
    "-a",
    "--approach",
    type=str,
    choices=[
        "process",
        "isolate",
        "faastion",
    ],
    required=True,
)
args = parser.parse_args()

approach = args.approach
workload = args.workload
ndomains = args.ndomains


def get_times(path):
    init_state = []
    steady_state = []
    try:
        with open(path, 'r') as file:
            half_point = workload//2
            lines = file.readlines()

            init_state = [float(line) for line in lines[1:half_point]]
            steady_state = [float(line) for line in lines[half_point:]]
    except FileNotFoundError:
        print(f"The file at {path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return init_state, steady_state


def calculate_avg_list(decimals_list):
    return [np.mean(values) for values in zip(*decimals_list)]


def write_to_file(domains_avg, phase):
    try:
        with open(f"results/{phase}-{approach}-{ndomains}.txt", "w") as file:
            for decimal in domains_avg:
                file.write(str(decimal) + "\n")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    init_list = []
    steady_list = []
    for i in range(1, args.ndomains + 1):
        init_avgs = []
        steady_avgs = []
        for j in range(1, 6):
            init_state, steady_state = get_times(PATH_TEMPLATE.format(approach=approach, n=i, run=j))
            init_avgs.append(init_state)
            steady_avgs.append(steady_state)

        init_list.append(calculate_avg_list(init_avgs))
        steady_list.append(calculate_avg_list(steady_avgs))
    
    init_domains = calculate_avg_list(init_list)
    steady_domains = calculate_avg_list(steady_list)

    write_to_file(init_domains, "init")
    write_to_file(steady_domains, "steady")

if __name__ == "__main__":
    main()