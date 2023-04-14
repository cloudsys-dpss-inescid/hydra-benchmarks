#!/usr/bin/python

import sys
import csv
import io
import matplotlib.pyplot as plt
import argparse

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


parser = argparse.ArgumentParser(description='Plot two-dimensional datapoints.')
parser.add_argument('-o', '--output', required=False)
parser.add_argument('-x', '--xlabel', required=False)
parser.add_argument('-y', '--ylabel', required=False)
parser.add_argument('-ymax', '--ymax', required=False)

args = parser.parse_args()

x, activeUsers, activeFunctions, cachedActiveUsers, cachedActiveFunctions, runningInvocations = read_stdin_xy()
first = x[0]
x = [elem - first for elem in x]

fig = plt.figure()
ax1 = fig.add_subplot(111)

ax1.scatter(x, activeUsers, s=1, label='Users')
ax1.scatter(x, activeFunctions, s=1, label='Functions')
ax1.scatter(x, cachedActiveUsers, s=1, label='Cached users')
ax1.scatter(x, cachedActiveFunctions, s=1, label='Cached functions')
ax1.scatter(x, runningInvocations, s=1, label='Invocations')

plt.legend(loc='upper left')

# Plot.
plt.ylim(ymin=0)#, ymax=float(args.ymax))
plt.xlim(xmin=0)

if args.xlabel is not None:
  plt.xlabel(args.xlabel)

if args.ylabel is not None:
  plt.ylabel(args.ylabel)

if args.output is not None:
  plt.savefig(args.output)
else:
  plt.show()

