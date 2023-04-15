#!/usr/bin/python

import sys
import csv
import io
import matplotlib
import matplotlib.pyplot as plt

# Syntax example: cat plot-data.txt | plot-simulation.py
# data.txt should be a file with six columns.


def read_stdin_xy():
  # Read input from stdin.
  input = sys.stdin.read()

  # Read string as a csv file (line by line, separated by a delimiter).
  reader = csv.reader(io.StringIO(input), delimiter=' ')

  x = []
  yActiveUsers = []
  yActiveFunctions = []
  yCachedActiveUsers = []
  yCachedActiveFunctions = []
  yRunningInvocations = []

  # For each line, split and add to x and or y.
  for cols in reader:
    try:
      xentry = float(cols[0])
      activeUsersEntry = float(cols[1])
      activeFunctionsEntry = float(cols[2])
      cachedActiveUsersEntry = float(cols[3])
      cachedActiveFunctionsEntry = float(cols[4])
      runningInvocationsEntry = float(cols[5])
      x.append(xentry)
      yActiveUsers.append(activeUsersEntry)
      yActiveFunctions.append(activeFunctionsEntry)
      yCachedActiveUsers.append(cachedActiveUsersEntry)
      yCachedActiveFunctions.append(cachedActiveFunctionsEntry)
      yRunningInvocations.append(runningInvocationsEntry)
    except Exception as e:
      print("Warning ignoring " + str(cols))
  return x, yActiveUsers, yActiveFunctions, yCachedActiveUsers, yCachedActiveFunctions, yRunningInvocations


x, activeUsers, activeFunctions, cachedActiveUsers, cachedActiveFunctions, runningInvocations = read_stdin_xy()
first = x[0]
x = [elem - first for elem in x]

# Convert from ms to sec
x = [elem/1000 for elem in x]

matplotlib.rcParams.update({'font.size': 16})
plt.rcParams["figure.figsize"] = (8, 5.5)
plt.xlabel('Time (seconds)')
plt.plot(x, activeUsers,           linewidth=3, linestyle=':', label='Active Users')
plt.plot(x, activeFunctions,       linewidth=3, linestyle='--', label='Active Functions')
plt.plot(x, runningInvocations,    linewidth=3, linestyle='-', label='Invocations')
plt.plot(x, cachedActiveUsers,     linewidth=3, linestyle=':', label='Cached Users')
plt.plot(x, cachedActiveFunctions, linewidth=3, linestyle='--', label='Cached Functions')
plt.yscale('log', base=10)
plt.ylim(ymin=0, ymax=2000)
plt.xlim(xmin=0)
plt.legend(loc='upper left', ncol=2, frameon=False)
plt.savefig("plot-azure-users-functions.pdf", bbox_inches='tight')
plt.savefig("plot-azure-users-functions.png", bbox_inches='tight')
plt.show()
