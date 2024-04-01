import matplotlib
import matplotlib.pyplot as plt
import numpy as np


width = 0.25
KA_labels = [
    "1 minute",
    "5 minutes",
    "10 minutes"
]
x = np.arange(len(KA_labels))


def get_avg_latency_for_KA_and_percentile(KA, percentile):
    # _, nc_np_latencies = np.genfromtxt(f'./{KA}/latency_no_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_np_latencies  = np.genfromtxt(f'./{KA}/latency_cache_no_pers_{percentile}.txt', delimiter=' ').transpose()
    _, c_p_latencies   = np.genfromtxt(f'./{KA}/latency_cache_pers_{percentile}.txt', delimiter=' ').transpose()
    return np.mean(c_np_latencies), np.mean(c_p_latencies)


def get_avg_memory_for_KA_and_percentile(KA, percentile):
    # nc_np_memory = np.loadtxt(f'./{KA}/memory_no_cache_no_pers_{percentile}.rss')
    c_np_memory  = np.loadtxt(f'./{KA}/memory_cache_no_pers_{percentile}.rss')
    c_p_memory   = np.loadtxt(f'./{KA}/memory_cache_pers_{percentile}.rss')
    return np.mean(c_np_memory), np.mean(c_p_memory)


def plot(perc):
    mem_cn_KA1_50, mem_cp_KA1_50 =   get_avg_memory_for_KA_and_percentile("KA1", perc)
    mem_cn_KA5_50, mem_cp_KA5_50 =   get_avg_memory_for_KA_and_percentile("KA5", perc)
    mem_cn_KA10_50, mem_cp_KA10_50 = get_avg_memory_for_KA_and_percentile("KA10", perc)

    lat_cn_KA1_50, lat_cp_KA1_50 =   get_avg_latency_for_KA_and_percentile("KA1", perc)
    lat_cn_KA5_50, lat_cp_KA5_50 =   get_avg_latency_for_KA_and_percentile("KA5", perc)
    lat_cn_KA10_50, lat_cp_KA10_50 = get_avg_latency_for_KA_and_percentile("KA10", perc)

    memory = [
        mem_cn_KA1_50 / mem_cp_KA1_50,
        mem_cn_KA5_50 / mem_cp_KA5_50,
        mem_cn_KA10_50 / mem_cp_KA10_50
    ]
    latency = [
        lat_cn_KA1_50 / lat_cp_KA1_50,
        lat_cn_KA5_50 / lat_cp_KA5_50,
        lat_cn_KA10_50 / lat_cp_KA10_50
    ]


    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()

    ax.bar(x + 0*width, memory,   width=width, hatch='*', label='Memory',  alpha=0.75)
    ax.bar(x + 1*width, latency,  width=width, hatch='O', label='Latency', alpha=0.75)

    ax.set_xlabel("Keep-Alive Period (min)")
    ax.set_ylabel("Improvement (times)")
    ax.set_xticks([position + width/2 for position in x], KA_labels)
    ax.set_axisbelow(True)

    # Ticks.
    ax.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator([1.0001]))
    ax.grid(which='minor', axis = 'y', linestyle = '-', color='r', linewidth = 1)
    ax.grid(which='major', axis = 'y', linestyle = '--', linewidth = 0.25)
    # plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)

    # # plt.yscale('log', base=10)
    ax.set_ylim(ymin=0, ymax=5)
    #ax.set_xlim(xmin=0)
    fig.set_figwidth(10)
    fig.set_figheight(5)

    ax.legend(ncol=5, loc='upper center')
    plt.savefig(f"improvement_{perc}.pdf", bbox_inches='tight')
    plt.savefig(f"improvement_{perc}.png", bbox_inches='tight')
    plt.show()


plot("25")
plot("50")
plot("75")
plot("90")
