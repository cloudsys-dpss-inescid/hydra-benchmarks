package org.graalvm.argo.dataset;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.LinkedList;
import java.util.List;
import java.util.TreeSet;
import java.util.stream.Collectors;

/**
 * This class loads an invocation trace and replays each invocation, one at a
 * time. Periodically, it will generate information regarding the number of
 * users, functions, and invocations that would be active on a real platform.
 */
public class InvocationTraceSimulator {

    protected Invocation createInvocation(String owner, String function, int memory, int duration, int timestamp) {
        return new Invocation(owner, function, memory, duration, timestamp);
    }

    protected List<Invocation> loadInvocations(String invocationsFile) {
        List<Invocation> invocations = new LinkedList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(invocationsFile))) {
            String line;
            String[] splitRow;
            br.readLine(); // To skip the header
            while ((line = br.readLine()) != null) {
                splitRow = line.split(InvocationTraceGenerator.DELIMITER);
                invocations.add(createInvocation(splitRow[0], splitRow[1], Integer.valueOf(splitRow[2]), Integer.valueOf(splitRow[3]), Integer.valueOf(splitRow[4])));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return invocations;
    }

    protected void evictTimedOutInvocations(TreeSet<? extends Invocation> activeInvocations, int timestamp, int keepalive) {
        List<Invocation> evict = new LinkedList<>();
        for (Invocation invocation : activeInvocations) {
            if (timestamp >= invocation.getEndTimestamp() + keepalive) {
                evict.add(invocation);
            } else {
                // The activeInvocations tree is ordered. If we fail the above check, later elements will also fail.
                break;
            }
        }
        activeInvocations.removeAll(evict);
    }

    // TODO - for these, I don't see a clear reason not to doit in a stream.
    protected Invocation findWarmInvocation(TreeSet<? extends Invocation> activeInvocations, int timestamp, String function) {
        for (Invocation invocation : activeInvocations) {
            if (timestamp < invocation.getEndTimestamp()) {
                continue;
            } else if (invocation.getFunction().equals(function)) {
                return invocation;
            }
        }
        return null;
    }

    private void updateStatistics(
            TreeSet<Invocation> activeInvocations,
            List<OutputEntry> statistics,
            int currentTimestamp,
            int previousTimestamp,
            int lastInvocationsProcessed,
            int coldStarts,
            int invocationsProcessed) {

        List<Invocation> runningInvocations = activeInvocations.parallelStream().filter(i -> i.getEndTimestamp() > currentTimestamp).collect(Collectors.toList());
        int runningUsers = (int) runningInvocations.parallelStream().map(Invocation::getOwner).distinct().count();
        int runningFunctions  = (int) runningInvocations.parallelStream().map(Invocation::getFunction).distinct().count();
        int runningInvocationsFootprint = (int) runningInvocations.parallelStream().mapToInt(Invocation::getMemory).sum();

        int totalUsers = (int) activeInvocations.parallelStream().map(Invocation::getOwner).distinct().count();
        int totalFunctions = (int) activeInvocations.parallelStream().map(Invocation::getFunction).distinct().count();

        int cachedUsers = totalUsers - runningUsers;
        int cachedFunctions = totalFunctions - runningFunctions;
        int cachedInvocationsFootprint = activeInvocations.parallelStream().filter(i -> i.getEndTimestamp() < currentTimestamp).mapToInt(Invocation::getMemory).sum();

        statistics.add(new OutputEntry(
                currentTimestamp,
                invocationsProcessed - lastInvocationsProcessed,
                coldStarts,
                runningUsers,
                runningFunctions,
                runningInvocations.size(),
                runningInvocationsFootprint,
                cachedUsers,
                cachedFunctions,
                cachedInvocationsFootprint));
    }

    protected List<OutputEntry> simulateInvocations(List<Invocation> invocations, int keepalive, int interval) {
        TreeSet<Invocation> activeInvocations = new TreeSet<>(Invocation.comparator());
        List<OutputEntry> statistics = new LinkedList<>();
        int invocationsProcessed = 0;
        int currentTimestamp = 0;
        int previousTimestamp = 0;
        int lastInvocationsProcessed = 0;
        int coldStarts = 0;

        System.err.println("Simulating trace with " + invocations.size() + " invocations and keepalive of " + keepalive);
        for (Invocation currentInvocation : invocations) {
            currentTimestamp = currentInvocation.getTimestamp();

            // Remove invocations that have past their keep alive time.
            evictTimedOutInvocations(activeInvocations, currentTimestamp, keepalive);

            // We try to find an inactive invocation that can be replaced with the new one.
            Invocation warm = findWarmInvocation(activeInvocations, currentTimestamp, currentInvocation.getFunction());
            if (warm == null) {
                coldStarts++;
            } else {
                activeInvocations.remove(warm);
            }

            // Add invocation to array of active invocations.
            activeInvocations.add(currentInvocation);
            invocationsProcessed++;

            if (currentTimestamp - previousTimestamp > interval) {
                // Calculate and update statistics.
                updateStatistics(activeInvocations, statistics, currentTimestamp, previousTimestamp, lastInvocationsProcessed, coldStarts, invocationsProcessed);

                // Reset values until the next round.
                previousTimestamp = currentTimestamp;
                lastInvocationsProcessed = invocationsProcessed;
                coldStarts = 0;
            }

            // Progress update...
            if (invocationsProcessed  % Math.max(invocations.size() / 100, 1) == 0) {
                System.err.println(String.format("Processed %s (%.2f %%)", invocationsProcessed, ((float) invocationsProcessed / (float)invocations.size() * 100)));
            }
        }

        // Final update to statistics.
        updateStatistics(activeInvocations, statistics, currentTimestamp, previousTimestamp, lastInvocationsProcessed, coldStarts, invocationsProcessed);

        return statistics;
    }

    public List<OutputEntry> simulate(String inputFile, int keepAlive, int sampleInterval) {
        List<Invocation> invocations = loadInvocations(inputFile);
        return simulateInvocations(invocations, keepAlive, sampleInterval);
    }
}
