import pandas as pd
import sys
import os


def process(dataset_id):
    result = pd.DataFrame(columns = ["HashOwner", "HashFunction", "AverageAllocatedMb", "AverageDuration", "Timestamp"])
    for file in os.listdir("."):
        if file.startswith(f"result_{dataset_id}_split_"):
            df = pd.read_csv(file)
            result = pd.concat([result, df], ignore_index=True, axis=0)
    result = result.sort_values(by=["Timestamp"], ascending=True)
    result.to_csv("result_" + dataset_id + ".csv", encoding='utf-8', index=False)


if __name__ == "__main__":
    process(sys.argv[1])
