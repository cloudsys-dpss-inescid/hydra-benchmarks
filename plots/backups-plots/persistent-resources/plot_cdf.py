import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def get_latency_for_KA_and_percentile(KA, percentile):
    # _, nc_np_latencies = np.genfromtxt(f'./{KA}/latency_no_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_np_latencies  = np.genfromtxt(f'./{KA}/latency_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_p_latencies   = np.genfromtxt(f'./{KA}/latency_cache_pers_{percentile}.txt', delimiter=' ').transpose()
    return c_np_latencies, c_p_latencies


def plot(ka, perc):
    lat_cn, lat_cp = get_latency_for_KA_and_percentile(ka, perc)
    x_lat_cn = np.sort(lat_cn)
    x_lat_cp = np.sort(lat_cp)

    y_lat_cn = np.arange(len(lat_cn)) / float(len(lat_cn))
    y_lat_cp = np.arange(len(lat_cp)) / float(len(lat_cp))

    if perc == "25":
        y_lat_cn = [0, 0.5, 1]
        y_lat_cp = [0, 0.5, 1]

    plt.rcParams.update({'font.size': 12})
    fig, ax = plt.subplots()

    ax.plot(x_lat_cp, y_lat_cp, linewidth=3, linestyle="solid", label='With Persistent Resources')
    ax.plot(x_lat_cn, y_lat_cn, linewidth=3, linestyle="dashed", label='Without Persistent Resources')

    ax.set_xlabel("Request Latency (ms)")
    ax.set_ylabel("CDF")

    yticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
    ax.set_yticks(yticks)
    ax.grid()

    ax.set_ylim(ymin=0, ymax=1)
    ax.set_xlim(xmin=0)
    fig.set_figwidth(4)
    fig.set_figheight(3)

    ax.legend(ncol=1, loc='lower center')
    plt.savefig(f"cdf_latency_{ka}_{perc}.pdf", bbox_inches='tight')
    plt.savefig(f"cdf_latency_{ka}_{perc}.png", bbox_inches='tight')
    plt.show()


plot("KA10", "25")
plot("KA10", "50")
plot("KA10", "75")
plot("KA10", "90")
