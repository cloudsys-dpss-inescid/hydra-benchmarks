import argparse
import matplotlib.pyplot as plt
import numpy as np

file_path_template = 'logs/{approach}-{n}-{run}.log'

def get_decimals(path):
    decimals = []
    try:
        with open(path, 'r') as file:
            for line in file.readlines():
                decimals.append(float(line))
    except FileNotFoundError:
        print(f"The file at {path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return decimals

def calculate_avg_list(decimals_list):
    return [np.mean(values) for values in zip(*decimals_list)]

def write_to_file(domains_avg, ndomains, approach):
    try:
        with open(f"results/{approach}-{ndomains}.txt", "w") as file:
            for decimal in domains_avg:
                file.write(str(decimal) + "\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ndomains", type=int, required=True)
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

    decimals_list = []
    for i in range(1, args.ndomains + 1):
        decimals_avg = []

        for j in range(1, 6):
            decimals_avg.append(get_decimals(file_path_template.format(approach=args.approach, n=i, run=j)))

        decimals_list.append(calculate_avg_list(decimals_avg))
    
    domains_avg = calculate_avg_list(decimals_list)
    
    plt.plot(list(range(1,len(domains_avg)+1)), domains_avg, label = f"{args.ndomains} domains")
    plt.scatter(list(range(1,len(domains_avg)+1)), domains_avg)
    plt.legend()
    plt.ylabel("Time of Execution (us)")
    plt.xlabel("No. of Invocations")
    plt.title("Execution on Graal Native Image (Hello World)")
    plt.savefig(f'results/HelloWorld-{args.ndomains}.png')

    write_to_file(domains_avg, args.ndomains, args.approach)

if __name__ == "__main__":
    main()