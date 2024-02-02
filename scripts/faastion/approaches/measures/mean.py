import numpy as np

def get_average_time(path):
    times = []
    try:
        with open(path, 'r') as file:
            for time in file:
                times.append(int(time))
    except Exception as e:
        print(f"An error occurred: {e}")

    return times[1:]

def main():
    approaches = ["isolate", "process", "faastion"]
    gv_path_template = "results/{approach}-gv.log"
    sb_path_template = "results/{approach}-sb.log"

    for approach in approaches:
        gv_times = get_average_time(gv_path_template.format(approach=approach))
        sb_times = get_average_time(sb_path_template.format(approach=approach))
        
        avg_times = []
        for index, gv_time in enumerate(gv_times):
            avg_times.append(gv_time - sb_times[index])

        avg = np.mean(avg_times)
        std = np.std(avg_times)
        print(f"Average time for {approach}: {round(avg, 4)} (us)")
        print(f"Standard deviation for {approach}: {round(std, 4)} (us)")

if __name__ == "__main__":
    main()

