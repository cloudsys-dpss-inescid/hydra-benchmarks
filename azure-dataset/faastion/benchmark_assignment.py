import csv

def read_csv(filename):
    data = []
    with open(filename, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data


def main():
    filename = 'example.csv'  
    csv_data = read_csv(filename)
    num_buckets = 10
    buckets = [[] for _ in range(num_buckets)]
    times = [[] for _ in range(num_buckets)]
    for value in csv_data:
        bucket_number = int(value[2]) % num_buckets
        buckets[bucket_number].append(value[2])
		times[bucket_number].append(value[4])


    for i, bucket in enumerate(buckets):
        print(f"Bucket {i+1}: {bucket}")

if __name__ == "__main__":
    main()
