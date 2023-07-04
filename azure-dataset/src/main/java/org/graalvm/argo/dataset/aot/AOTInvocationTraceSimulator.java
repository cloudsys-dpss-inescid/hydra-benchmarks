package org.graalvm.argo.dataset.aot;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.TreeSet;
import java.util.stream.Collectors;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.graalvm.argo.dataset.Invocation;
import org.graalvm.argo.dataset.InvocationTraceGenerator;
import org.graalvm.argo.dataset.InvocationTraceSimulator;
import org.graalvm.argo.dataset.OutputEntry;
import org.graalvm.argo.dataset.utils.ColdStartSlidingWindow;

/**
 * This class is an extension of InvocationTraceSimulator that also
 * allows for simulating AOT optimizations.
 */
public class AOTInvocationTraceSimulator extends InvocationTraceSimulator {

    /**
     * Minimum number of cold starts within a period.
     */
    private static final int AOT_OPTIMIZATION_THRESHOLD = 10;

    /**
     * Period during which we count number of cold starts (in ms).
     */
    private static final int SLIDING_WINDOW_PERIOD = 60000;

    @Override
    protected Invocation createInvocation(String owner, String function, int memory, int duration, int timestamp) {
        return new AOTInvocation(owner, function, memory, duration, timestamp);
    }

    private void updateStatistics(
            TreeSet<AOTInvocation> activeInvocations,
            List<OutputEntry> statistics,
            int currentTimestamp,
            int previousTimestamp,
            int lastInvocationsProcessed,
            int coldStarts,
            int optimizedColdStarts,
            int invocationsProcessed) {

        List<AOTInvocation> runningInvocations = activeInvocations.parallelStream().filter(i -> i.getEndTimestamp() > currentTimestamp).collect(Collectors.toList());
        int runningUsers = (int) runningInvocations.parallelStream().map(AOTInvocation::getOwner).distinct().count();
        int runningFunctions  = (int) runningInvocations.parallelStream().map(AOTInvocation::getFunction).distinct().count();
        int runningOptimizedFunctions  = (int) runningInvocations.parallelStream().filter(AOTInvocation::isOptimized).map(AOTInvocation::getFunction).distinct().count();
        int runningInvocationsFootprint = (int) runningInvocations.parallelStream().mapToInt(AOTInvocation::getMemory).sum();

        int totalUsers = (int) activeInvocations.parallelStream().map(AOTInvocation::getOwner).distinct().count();
        int totalFunctions = (int) activeInvocations.parallelStream().map(AOTInvocation::getFunction).distinct().count();

        int cachedUsers = totalUsers - runningUsers;
        int cachedFunctions = totalFunctions - runningFunctions;
        int cachedInvocationsFootprint = activeInvocations.parallelStream().filter(i -> i.getEndTimestamp() < currentTimestamp).mapToInt(AOTInvocation::getMemory).sum();

        statistics.add(new AOTOutputEntry(
                currentTimestamp,
                invocationsProcessed - lastInvocationsProcessed,
                coldStarts,
                optimizedColdStarts,
                runningUsers,
                runningFunctions,
                runningOptimizedFunctions,
                runningInvocations.size(),
                runningInvocationsFootprint,
                cachedUsers,
                cachedFunctions,
                cachedInvocationsFootprint));
    }

    @Override
    protected List<OutputEntry> simulateInvocations(List<Invocation> invocations, int keepalive, int interval) {
        TreeSet<AOTInvocation> activeInvocations = new TreeSet<>(AOTInvocation.comparator());
        List<OutputEntry> statistics = new LinkedList<>();
        ColdStartSlidingWindow window = new ColdStartSlidingWindow(AOT_OPTIMIZATION_THRESHOLD, SLIDING_WINDOW_PERIOD);
        String currentFunction;
        int invocationsProcessed = 0;
        int currentTimestamp = 0;
        int previousTimestamp = 0;
        int lastInvocationsProcessed = 0;
        int coldStarts = 0;
        int optimizedColdStarts = 0;

        System.err.println("Simulating trace with " + invocations.size() + " invocations and keepalive of " + keepalive);
        for (Invocation baseCurrentInvocation : invocations) {
            AOTInvocation currentInvocation = (AOTInvocation) baseCurrentInvocation;
            currentTimestamp = currentInvocation.getTimestamp();
            currentFunction = currentInvocation.getFunction();

            // Remove invocations that have past their keep alive time.
            evictTimedOutInvocations(activeInvocations, currentTimestamp, keepalive);

            // We try to find an inactive invocation that can be replaced with the new one.
            Invocation warm = findWarmInvocation(activeInvocations, currentTimestamp, currentFunction);
            if (warm == null) {
                coldStarts++;
                if (window.optimized(currentFunction) || window.worthOptimizing(currentFunction, currentTimestamp)) {
                    optimizedColdStarts++;
                    // Cold start happened, but the function is optimized.
                    currentInvocation.optimize();
                } else {
                    window.add(currentFunction, currentTimestamp);
                }
            } else {
                activeInvocations.remove(warm);
                // Reuse memory and optimization status of the warm invocation instead of always using unoptimized.
                currentInvocation.setOptimizedMemory((AOTInvocation) warm);
            }

            // Add invocation to array of active invocations.
            activeInvocations.add(currentInvocation);
            invocationsProcessed++;

            if (currentTimestamp - previousTimestamp > interval) {
                // Calculate and update statistics.
                updateStatistics(activeInvocations, statistics, currentTimestamp, previousTimestamp, lastInvocationsProcessed, coldStarts, optimizedColdStarts, invocationsProcessed);

                // Reset values until the next round.
                previousTimestamp = currentTimestamp;
                lastInvocationsProcessed = invocationsProcessed;
                coldStarts = 0;
                optimizedColdStarts = 0;
            }

            // Progress update...
            if (invocationsProcessed  % Math.max(invocations.size() / 100, 1) == 0) {
                System.err.println(String.format("Processed %s (%.2f %%)", invocationsProcessed, ((float) invocationsProcessed / (float)invocations.size() * 100)));
            }
        }

        // Final update to statistics.
        updateStatistics(activeInvocations, statistics, currentTimestamp, previousTimestamp, lastInvocationsProcessed, coldStarts, optimizedColdStarts, invocationsProcessed);

        return statistics;
    }
}
