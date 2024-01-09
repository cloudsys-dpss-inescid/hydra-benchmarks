import matplotlib.pyplot as plt
import numpy as np

# Open a file in read mode ('r')
file_path = 'ab-iso.log'
file_path_2 = 'ab-proc.log'
file_path_3 = 'ab-mem.log'
ans = []
ans_process = []
ans_mem = []
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

try:
    with open(file_path_2, 'r') as file:
        # Read the file line by line
        for line in file:
            if "Time" in line and "concurrent" not in line:
                ans_process.append(line.strip())
except FileNotFoundError:
    print(f"The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

try:
    with open(file_path_3, 'r') as file:
        # Read the file line by line
        for line in file:
            if "Time" in line and "concurrent" not in line:
                ans_mem.append(line.strip())
except FileNotFoundError:
    print(f"The file at {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")


decimals = []
for string in ans:
    words = string.split()
    decimals.append(float(words[3]))

decimals_2 = []
for string in ans_process:
    words = string.split()
    decimals_2.append(float(words[3]))

decimals_3 = []
for string in ans_mem:
    words = string.split()
    decimals_3.append(float(words[3]))




plt.plot(list(range(1,len(decimals)+1)), decimals,label = "Isolate")
plt.plot(list(range(1,len(decimals_2)+1)), decimals_2, label = "Process")
plt.plot(list(range(1,len(decimals_3)+1)), decimals_3, label = "Memory Isolation")
plt.scatter(list(range(1,len(decimals)+1)), decimals)
plt.scatter(list(range(1,len(decimals_2)+1)), decimals_2)
plt.scatter(list(range(1,len(decimals_3)+1)), decimals_3)
plt.legend()
plt.ylabel("Time of Execution (ms)")
plt.xlabel("No. of Invocations")
plt.title("Execution on Graal Native Image (Hello World)")
plt.savefig('HelloWorld.png')