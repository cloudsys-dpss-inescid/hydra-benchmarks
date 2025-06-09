benchmark_labels = ["js/html","js/hw","js/upload","jv/hash","jv/hw","jv/http","py/bfs","py/compress","py/dna","py/html","py/hw","py-mst","py/pr","py/tn","py/upload"]
process_times = [397042,361454,485439,181403,39700,184793,1262066,2269484,2751807,3125743,1209698,1207131,3780183,2043909,2672652]

normal_labels = ["js/html","js/hw","js/tn","js/upload","jv/cy","jv/hash","jv/hw","jv/http","jv/vp","py/bfs","py/compress","py/dna","py/html","py/hw","py-mst","py/pr","py/tn","py/upload"]
normal_times = [26807,8236,167559,11123,682781,3645,1426,3858,1538564,204732,1878983,1174860,1336492,197116,208333,2008274,725520,1216685,2235124]
overhead = []

for e in normal_labels:
    if e in benchmark_labels:
        ind_n = normal_labels.index(e)
        ind_b = benchmark_labels.index(e)
        percentage = process_times[ind_b] / normal_times[ind_n]
        overhead.append(percentage)
    else:
        print(e + " not found in normal_labels")

print()
pretty = [round(x, 2) for x in overhead]
print(benchmark_labels)
print(pretty)

print()
latex  = ""
latex += "\\begin{tabular}{"
latex += "c" * len(pretty) # 'c' for center numbers
latex += "}"
latex += "\n"

for e in benchmark_labels[:-1]:
    latex += e
    latex += " & "
latex += benchmark_labels[-1]
latex += " \\\\\n"

for e in pretty[:-1]:
    latex += str(e)
    latex += " & "
    
latex += str(pretty[-1])
latex += " \\\\\n"

latex += "\\end{tabular}"
print(latex)
