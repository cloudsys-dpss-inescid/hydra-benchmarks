import csv
import argparse

def read_csv(filename):
	data = []
	with open(filename, 'r', newline='') as csvfile:
		csv_reader = csv.reader(csvfile)
		for row in csv_reader:
			data.append(row)
	return data

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument(
 		"-f", 
		"--num-functions", 
		type=int, 
		dest="num_functions", 
		default=5,
		help="Number of functions"
	)

	parser.add_argument(
		"-o",
		"--output",
		type=str,
		default="output.csv",
		help="Output file path",
	)

	args = parser.parse_args()
	return args.num_functions, args.output 

def main():
	num_functions, output_file = parse_args()
	filename = '../result.csv'
	csv_data = read_csv(filename)
    
	first_timestamp = int(csv_data[1][4])
	with open(output_file, 'w') as file:
		for value in csv_data[1:]:
			function_number = str(int(value[1], 16) % num_functions)
			timestamp = str(int(value[4]) - first_timestamp)
			file.write(function_number + "," + timestamp + "\n")

if __name__ == "__main__":
	main()
