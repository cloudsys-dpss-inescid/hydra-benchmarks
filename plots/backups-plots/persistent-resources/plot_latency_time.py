import matplotlib
import matplotlib.pyplot as plt
import numpy as np


ka1_nc_np_25_timestamps, ka1_nc_np_25_latencies = np.genfromtxt('./KA1/latency_no_cache_no_pers_25.txt', delimiter=' ').transpose()
ka1_nc_np_50_timestamps, ka1_nc_np_50_latencies = np.genfromtxt('./KA1/latency_no_cache_no_pers_50.txt', delimiter=' ').transpose()
ka1_nc_np_75_timestamps, ka1_nc_np_75_latencies = np.genfromtxt('./KA1/latency_no_cache_no_pers_75.txt', delimiter=' ').transpose()
ka1_nc_np_90_timestamps, ka1_nc_np_90_latencies = np.genfromtxt('./KA1/latency_no_cache_no_pers_90.txt', delimiter=' ').transpose()

ka1_c_np_25_timestamps, ka1_c_np_25_latencies = np.genfromtxt('./KA1/latency_cache_no_pers_25.txt', delimiter=' ').transpose()
ka1_c_np_50_timestamps, ka1_c_np_50_latencies = np.genfromtxt('./KA1/latency_cache_no_pers_50.txt', delimiter=' ').transpose()
ka1_c_np_75_timestamps, ka1_c_np_75_latencies = np.genfromtxt('./KA1/latency_cache_no_pers_75.txt', delimiter=' ').transpose()
ka1_c_np_90_timestamps, ka1_c_np_90_latencies = np.genfromtxt('./KA1/latency_cache_no_pers_90.txt', delimiter=' ').transpose()

ka1_c_p_25_timestamps, ka1_c_p_25_latencies = np.genfromtxt('./KA1/latency_cache_pers_25.txt', delimiter=' ').transpose()
ka1_c_p_50_timestamps, ka1_c_p_50_latencies = np.genfromtxt('./KA1/latency_cache_pers_50.txt', delimiter=' ').transpose()
ka1_c_p_75_timestamps, ka1_c_p_75_latencies = np.genfromtxt('./KA1/latency_cache_pers_75.txt', delimiter=' ').transpose()
ka1_c_p_90_timestamps, ka1_c_p_90_latencies = np.genfromtxt('./KA1/latency_cache_pers_90.txt', delimiter=' ').transpose()

ka1_lowest_timestamp = np.min([np.min(ka1_nc_np_25_timestamps), np.min(ka1_nc_np_50_timestamps), np.min(ka1_nc_np_75_timestamps), np.min(ka1_nc_np_90_timestamps)])

ka1_nc_np_25_timestamps = (ka1_nc_np_25_timestamps  - ka1_lowest_timestamp) / 1000
ka1_nc_np_50_timestamps = (ka1_nc_np_50_timestamps  - ka1_lowest_timestamp) / 1000
ka1_nc_np_75_timestamps = (ka1_nc_np_75_timestamps  - ka1_lowest_timestamp) / 1000
ka1_nc_np_90_timestamps = (ka1_nc_np_90_timestamps  - ka1_lowest_timestamp) / 1000
ka1_c_np_25_timestamps  = (ka1_c_np_25_timestamps   - ka1_lowest_timestamp) / 1000
ka1_c_np_50_timestamps  = (ka1_c_np_50_timestamps   - ka1_lowest_timestamp) / 1000
ka1_c_np_75_timestamps  = (ka1_c_np_75_timestamps   - ka1_lowest_timestamp) / 1000
ka1_c_np_90_timestamps  = (ka1_c_np_90_timestamps   - ka1_lowest_timestamp) / 1000
ka1_c_p_25_timestamps   = (ka1_c_p_25_timestamps    - ka1_lowest_timestamp) / 1000
ka1_c_p_50_timestamps   = (ka1_c_p_50_timestamps    - ka1_lowest_timestamp) / 1000
ka1_c_p_75_timestamps   = (ka1_c_p_75_timestamps    - ka1_lowest_timestamp) / 1000
ka1_c_p_90_timestamps   = (ka1_c_p_90_timestamps    - ka1_lowest_timestamp) / 1000

plt.rcParams.update({'font.size': 22})
fig, ax = plt.subplots()

ax.plot(ka1_nc_np_90_timestamps, ka1_nc_np_90_latencies, linewidth=3, linestyle="solid", label='nn')
ax.plot( ka1_c_np_90_timestamps,  ka1_c_np_90_latencies, linewidth=3, linestyle="dashed", label='cn')
ax.plot(  ka1_c_p_90_timestamps,   ka1_c_p_90_latencies, linewidth=3, linestyle="dotted", label='cp')

ax.set_xlabel("Time (s)")
ax.set_ylabel("Latency (us)")

# plt.yscale('log', base=10)
ax.set_ylim(ymin=0)
ax.set_xlim(xmin=0)
fig.set_figwidth(10)
fig.set_figheight(5)

ax.legend(ncol=5, loc='upper center')
plt.savefig("footprint.pdf", bbox_inches='tight')
plt.savefig("footprint.png", bbox_inches='tight')
plt.show()
