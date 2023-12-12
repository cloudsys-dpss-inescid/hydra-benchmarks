import matplotlib.pyplot as plt
import numpy as np

# Open a file in read mode ('r')
file_path = '/tmp/ab.log'

ans = []

try:
    with open(file_path, 'r') as file:
        # Read the file line by line
        for line in file:
            if "Time" in line and "concurrent" not in line:
                ans.append(line.strip())
except FileNotFoundError:
    print(f"The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

decimals = []
for string in ans:
    words = string.split()
    decimals.append(float(words[3]))



plt.plot(list(range(1,len(decimals)+1)), decimals)  # Plot the chart
plt.show()
plt.ylabel("Time of Execution (ms)")
plt.xlabel("No. of Invocations")
plt.title("Execution using Memory Isolation")
plt.savefig('memisolation.png')