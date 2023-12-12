import matplotlib.pyplot as plt
import numpy as np
import argparse

def read_file(run, file_path):
    try:
        with open(file_path.format(run=run), 'r') as file:
            lines = file.readlines()
            return [float(lines[i].split()[3]) for i in range(0, 20, 2)]
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workload", type=int, default=50)
    args = parser.parse_args()

    file_path = '/tmp/ab-{run}.log'
    means = []

    for run in range(1, args.workload + 1):
        values = read_file(run, file_path)
        if values:
            means.append(np.mean(values))

    plt.plot(range(1, len(means) + 1), means)
    plt.ylabel("Time of Execution (ms)")
    plt.xlabel("No. of Invocations")
    plt.title("Execution using Memory Isolation")
    plt.show()
    plt.savefig('memisolation.png')

if __name__ == "__main__":
    main()
