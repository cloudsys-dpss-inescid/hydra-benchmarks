# The script must be placed in the same directory with dataset's csv files
# # Example of use:
# python3 process_dataset.py d01

import sys
import pandas as pd
import numpy as np


def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r\n"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print('\n')


def get_timestamps(invocations):
    df_columns = ["HashFunction", "AverageAllocatedMb", "AverageDuration", "Timestamp"]
    result = pd.DataFrame(columns = df_columns)
    minutes = pd.DataFrame({'minute' : map(str, np.arange(1, 1441, 1)), 'minute_timestamp_ms' : np.arange(0, 86340001, 60000)})

    progress_total = invocations.shape[0]
    printProgressBar(0, progress_total, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for index, row in invocations.iterrows():
        # minute_row[0] - minute, minute_row[1] - timestamp of the beginning of this minute
        records = [np.random.randint(minute_row[1], (minute_row[1] + 60000), size=row[minute_row[0]]) for minute_row in zip(minutes['minute'], minutes['minute_timestamp_ms'])]
        records = np.concatenate(records).ravel()    # flatten list of ndarrays to list of numbers (timestamps)
        records = [[row.HashFunction, row.AverageAllocatedMb, row.AverageDuration, r] for r in records]
        temp = pd.DataFrame(records, columns = df_columns)
        result = pd.concat([result, temp], ignore_index=True, axis=0)
        printProgressBar(index, progress_total, prefix = 'Progress:', suffix = f'Complete ({index})', length = 50)
    return result.sort_values(by=["Timestamp"], ascending=True)


def add_average_memory(invocations, dataset_id):
    memory = pd.read_csv("app_memory_percentiles.anon." + dataset_id + ".csv")
    avg_memories = []
    indexes_to_drop = []
    for index, row in invocations.iterrows():
        memory_record = memory[(memory.HashOwner == row.HashOwner) & (memory.HashApp == row.HashApp)]
        if memory_record.shape[0] == 1: # we have exactly one record about this combination of owner and app
            avg_memories.append(memory_record.iloc[0].AverageAllocatedMb)
        else:                           # we have zero or more than one records about this combination -> ambiguity
            indexes_to_drop.append(index)
    invocations = invocations.drop(indexes_to_drop)
    invocations["AverageAllocatedMb"] = avg_memories
    return invocations


def add_average_duration(invocations, dataset_id):
    duration = pd.read_csv("function_durations_percentiles.anon." + dataset_id + ".csv")
    avg_durations = []
    indexes_to_drop = []
    for index, row in invocations.iterrows():
        duration_record = duration[(duration.HashOwner == row.HashOwner) & (duration.HashApp == row.HashApp) & (duration.HashFunction == row.HashFunction)]
        if duration_record.shape[0] == 1: # we have exactly one record about this combination of owner and app
            avg_durations.append(duration_record.iloc[0].Average)
        else:                             # we have zero or more than one records about this combination -> ambiguity
            indexes_to_drop.append(index)
    invocations = invocations.drop(indexes_to_drop)
    invocations["AverageDuration"] = avg_durations
    return invocations


def process(dataset_id):
    invocations = pd.read_csv("invocations_per_function_md.anon." + dataset_id + ".csv")
    print("Shape of dataset before changes:         ", invocations.shape)
    invocations = add_average_memory(invocations, dataset_id)
    print("Shape of dataset after adding memory:    ", invocations.shape)
    invocations = add_average_duration(invocations, dataset_id)
    print("Shape of dataset after adding durations: ", invocations.shape)
    result = get_timestamps(invocations)
    print("\nCompleted calculating timestamps!")
    result.to_csv("result." + dataset_id + ".csv", encoding='utf-8', index=False)


if __name__ == "__main__":
    process(sys.argv[1])
