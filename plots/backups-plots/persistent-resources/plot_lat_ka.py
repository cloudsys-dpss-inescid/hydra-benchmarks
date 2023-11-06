import matplotlib
import matplotlib.pyplot as plt
import numpy as np


KA_labels = [
    "1 minute",
    "5 minutes",
    "10 minutes"
]
x = [1, 5, 10]


def get_avg_latency_for_KA_and_percentile(KA, percentile):
    # _, nc_np_latencies = np.genfromtxt(f'./{KA}/latency_no_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_np_latencies  = np.genfromtxt(f'./{KA}/latency_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_p_latencies   = np.genfromtxt(f'./{KA}/latency_cache_pers_{percentile}.txt', delimiter=' ').transpose()
    return np.mean(c_np_latencies), np.mean(c_p_latencies)


def plot(perc):
    lat_cn_KA1, lat_cp_KA1 =   get_avg_latency_for_KA_and_percentile("KA1", perc)
    lat_cn_KA5, lat_cp_KA5 =   get_avg_latency_for_KA_and_percentile("KA5", perc)
    lat_cn_KA10, lat_cp_KA10 = get_avg_latency_for_KA_and_percentile("KA10", perc)
    lat_cn = [lat_cn_KA1, lat_cn_KA5, lat_cn_KA10]
    lat_cp = [lat_cp_KA1, lat_cp_KA5, lat_cp_KA10]

    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    ax.plot(x, lat_cp, linewidth=3, linestyle="solid", label='With Persistent Resources')
    ax.plot(x, lat_cn, linewidth=3, linestyle="dashed", label='Without Persistent Resources')

    ax.set_xlabel("Keep-Alive Period (min)")
    ax.set_ylabel("Average Request Latency (us)")

    xticks = [1, 5, 10]
    ax.set_xticks(xticks)
    ax.grid()

    # plt.yscale('log', base=10)
    if perc == "25" or perc == "90":
        y_max = np.max([np.max(lat_cn), np.max(lat_cp)])
        y_max += int(y_max * 0.50)
        ax.set_ylim(ymin=0, ymax=y_max)
    else:
        y_max = np.max([np.max(lat_cn), np.max(lat_cp)])
        y_max += int(y_max * 0.35)
        ax.set_ylim(ymin=0, ymax=y_max)
    ax.set_xlim(xmin=0, xmax=11)
    fig.set_figwidth(10)
    fig.set_figheight(5)

    ax.legend(ncol=1, loc='upper center')
    plt.savefig(f"latency_{perc}.pdf", bbox_inches='tight')
    plt.savefig(f"latency_{perc}.png", bbox_inches='tight')
    plt.show()

plot("25")
plot("50")
plot("75")
plot("90")
