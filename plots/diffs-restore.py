#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

benchmark_labels = ["js-dynamic-html","js-hello-world","js-uploader","jv-file-hashing","jv-hello-world","jv-httprequest","py-bfs","py-dna","py-hello-world","py-mst","py-pagerank","py-uploader"]
restore_times = [3582,1342,5358,3511,679,2389,4309,253763,3697,4044,201677,879649]
modified_times = [3809,1323,4988,2915,864,2255,3880,334710,2765,4653,218551,981040]

print(restore_times)
print(modified_times)
# Normalized entrypoint.
li = [x / y for x, y in zip(restore_times, modified_times)]
print("Normalized latency improvement:")
print(li)
print("Average latency improvement:" + str(sum(li) / len(li)) )

x = np.arange(len(benchmark_labels))
plt.rcParams.update({'font.size': 12})
fig, ax = plt.subplots()
width = 0.3

all_1 = [1] * len(restore_times)

ax.bar(x + 0*width, all_1,   width=width, hatch='...', label='Normal',  alpha=0.75)
ax.bar(x + 1*width, li,      width=width, hatch='|||', label='Restore',  alpha=0.75)

ax.set_xticks(x)
ax.set_xticklabels(benchmark_labels)
ax.legend()
plt.xticks(rotation = 45)
ax.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
ax.set_ylabel('Latency (us)')
ax.set_yscale('linear')
fig.set_figwidth(7)
fig.set_figheight(3)

plt.savefig("sandboxes-snapshot.pdf", bbox_inches='tight', dpi = 300)
plt.savefig("sandboxes-snapshot.png", bbox_inches='tight', dpi = 300)
