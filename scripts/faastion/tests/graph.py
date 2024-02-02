import matplotlib.pyplot as plt
import numpy as np

file_path_template = 'results/{phase}-{approach}-{requests}.txt'

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
    medians = {}
    for approach in ["isolate", "process", "faastion"]:
        medians[approach] = []
        for phase in ["init", "steady"]:
            times = []
            for n in range(2, 16):
                times.extend(get_decimals_list(file_path_template.format(phase=phase, approach=approach, requests=n)))
            medians[approach].append(round(np.median(times), 2))
            print(f"{approach} {phase} mean: {np.mean(times)} (us)")
    
    x = np.arange(2)
    width = 0.25
    multiplier = 0
    _, ax = plt.subplots(layout='constrained')

    for approach, values in medians.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, values, width, label=approach)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Time (us)')
    ax.set_title('Median time per approach')
    ax.set_xticks(x + width, ["Init", "Steady"])
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 160)

    plt.savefig('results/Median.png')


if __name__ == "__main__":
    main()