import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json


def get_data():
    pers = {}
    no_pers = {}
    with open('./result_pers.json') as json_file:
        pers = json.load(json_file)
    with open('./result_no_pers.json') as json_file:
        no_pers = json.load(json_file)
    return pers, no_pers


def plot():
    pers, no_pers = get_data()

    pers_keys = list(pers.keys())
    no_pers_keys = list(no_pers.keys())

    x_pers = list(map(int, pers_keys))
    x_pers.sort()
    x_no_pers = list(map(int, no_pers_keys))
    x_no_pers.sort()

    y_pers = []
    y_pers_err = []
    for size in x_pers:
        process_times = np.array(pers[str(size)]) / 1000 / 1000
        y_pers.append(np.mean(process_times))
        y_pers_err.append(np.std(process_times))
    y_no_pers = []
    y_no_pers_err = []
    for size in x_no_pers:
        process_times = np.array(no_pers[str(size)]) / 1000 / 1000
        y_no_pers.append(np.mean(process_times))
        y_no_pers_err.append(np.std(process_times))

    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()

    ax.errorbar(x_pers,    y_pers,    yerr=y_pers_err, linewidth=3, linestyle="solid", label='With Persistent Resources')
    ax.errorbar(x_no_pers, y_no_pers, yerr=y_no_pers_err, linewidth=3, linestyle="dashed", label='Without Persistent Resources')

    ax.set_xlabel("Query Size (rows)")
    ax.set_ylabel("Process Time (ms)")

    ax.set_xticks(x_pers)
    ax.grid()

    # ax.set_yscale('log')
    ax.set_xscale('log', base=2)
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=0)
    fig.set_figwidth(10)
    fig.set_figheight(5)

    ax.legend(ncol=1, loc='upper center')
    plt.savefig(f"overhead.pdf", bbox_inches='tight')
    plt.savefig(f"overhead.png", bbox_inches='tight')
    plt.show()

plot()
