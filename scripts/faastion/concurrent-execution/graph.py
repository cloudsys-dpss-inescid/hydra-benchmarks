import matplotlib.pyplot as plt
import numpy as np

file_path_template = 'results/{approach}-{requests}.txt'

def get_decimals_list(path):
    decimals = []
    try:
        with open(path, 'r') as file:
            decimals = [float(line) for line in file.readlines()[1:]]
    except FileNotFoundError:
        print(f"The file at {path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return decimals

def main():
    approaches = ["isolate", "process", "faastion"]

    medians = {}
    for approach in approaches:
        times = []
        for n in range(2, 16):
            times.extend(get_decimals_list(file_path_template.format(approach=approach, requests=n)))
        medians[approach] = round(np.median(times), 2)
        print(f"{approach} mean: {np.mean(times)} (us)")
    
    x = np.arange(1)
    width = 0.25
    multiplier = 0
    _, ax = plt.subplots(layout='constrained')

    for approach, median in medians.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, median, width, label=approach)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Time (us)')
    ax.set_title('Median time per approach')
    ax.set_xticks(x + width, ["Approaches"])
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 175)

    plt.savefig(f'results/Median.png')


if __name__ == "__main__":
    main()