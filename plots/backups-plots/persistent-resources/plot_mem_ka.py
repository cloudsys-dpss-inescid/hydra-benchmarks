import matplotlib
import matplotlib.pyplot as plt
import numpy as np


KA_labels = [
    "1",
    "5",
    "10"
]
x = [1, 5, 10]


def get_avg_memory_for_KA_and_percentile(KA, percentile):
    # nc_np_memory = np.loadtxt(f'./{KA}/memory_no_cache_no_pers_{percentile}.rss')
    c_np_memory  = np.loadtxt(f'./{KA}/memory_cache_no_pers_{percentile}.rss') / 1024
    c_p_memory   = np.loadtxt(f'./{KA}/memory_cache_pers_{percentile}.rss')    / 1024
    return np.mean(c_np_memory), np.mean(c_p_memory)


def plot(perc):
    mem_cn_KA1, mem_cp_KA1 =   get_avg_memory_for_KA_and_percentile("KA1", perc)
    mem_cn_KA5, mem_cp_KA5 =   get_avg_memory_for_KA_and_percentile("KA5", perc)
    mem_cn_KA10, mem_cp_KA10 = get_avg_memory_for_KA_and_percentile("KA10", perc)
    mem_cn = [mem_cn_KA1, mem_cn_KA5, mem_cn_KA10]
    mem_cp = [mem_cp_KA1, mem_cp_KA5, mem_cp_KA10]

    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()

    ax.plot(x, mem_cp, linewidth=3, linestyle="solid", label='With Persistent Resources')
    ax.plot(x, mem_cn, linewidth=3, linestyle="dashed", label='Without Persistent Resources')

    ax.set_xlabel("Keep-Alive Period (min)")
    ax.set_ylabel("Average Footprint (MB)")

    xticks = [1, 5, 10]
    ax.set_xticks(xticks)
    ax.grid()

    # plt.yscale('log', base=10)
    ax.set_ylim(ymin=0, ymax=100)
    ax.set_xlim(xmin=0, xmax=11)
    fig.set_figwidth(10)
    fig.set_figheight(5)

    ax.legend(ncol=1, loc='upper center')
    plt.savefig(f"memory_{perc}.pdf", bbox_inches='tight')
    plt.savefig(f"memory_{perc}.png", bbox_inches='tight')
    plt.show()

plot("25")
plot("50")
plot("75")
plot("90")
