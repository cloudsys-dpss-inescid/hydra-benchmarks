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
import org.graalvm.argo.dataset.utils.ColdStartSlidingWindow;

/**
 * This class loads an invocation trace and replays each invocation, one at a
 * time. Periodically, it will generate information regarding the number of
 * users, functions, and invocations that would be active on a real platform.
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

    public static void main(String[] args) throws Exception {
        Options options = InvocationTraceSimulator.prepareOptions();
        try {
            CommandLine cmd = new DefaultParser().parse(options, args);
            String inputfile = cmd.getOptionValue("input");
            int keepalive = Integer.parseInt(cmd.getOptionValue("keepalive", "600000"));
            List<AOTInvocation> invocations = loadInvocations(inputfile);
            List<AOTOutputEntry> output = simulateInvocationsWithAOTOptimization(invocations, keepalive, SAMPLE_INTERVAL);

            for (AOTOutputEntry entry : output) {
                System.out.println(entry);
            }
        } catch (ParseException e) {
            System.err.println(e.getMessage());
            new HelpFormatter().printHelp("utility-name", options);
        }
    }

    private static List<AOTInvocation> loadInvocations(String invocationsFile) {
        List<AOTInvocation> invocations = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(invocationsFile))) {
            String line;
            String[] splitRow;
            br.readLine(); // To skip the header
            while ((line = br.readLine()) != null) {
                splitRow = line.split(InvocationTraceGenerator.DELIMITER);
                invocations.add(new AOTInvocation(splitRow[0], splitRow[1], Integer.valueOf(splitRow[2]), Integer.valueOf(splitRow[3]), Integer.valueOf(splitRow[4])));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return invocations;
    }

    private static void updateStatistics(
            TreeSet<AOTInvocation> activeInvocations,
            List<AOTOutputEntry> statistics,
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

    public static List<AOTOutputEntry> simulateInvocationsWithAOTOptimization(List<AOTInvocation> invocations, int keepalive, int interval) throws Exception {
        TreeSet<AOTInvocation> activeInvocations = new TreeSet<>(AOTInvocation.comparator());
        List<AOTOutputEntry> statistics = new LinkedList<>();
        ColdStartSlidingWindow window = new ColdStartSlidingWindow(AOT_OPTIMIZATION_THRESHOLD, SLIDING_WINDOW_PERIOD);
        String currentFunction;
        int invocationsProcessed = 0;
        int currentTimestamp = 0;
        int previousTimestamp = 0;
        int lastInvocationsProcessed = 0;
        int coldStarts = 0;
        int optimizedColdStarts = 0;

        System.err.println("Simulating trace with " + invocations.size() + " invocations and keepalive of " + keepalive);
        for (AOTInvocation currentInvocation : invocations) {
            currentTimestamp = currentInvocation.getTimestamp();
            currentFunction = currentInvocation.getFunction();

            // Remove invocations that have past their keep alive time.
            InvocationTraceSimulator.evictTimedOutInvocations(activeInvocations, currentTimestamp, keepalive);

            // We try to find an inactive invocation that can be replaced with the new one.
            Invocation warm = InvocationTraceSimulator.findWarmInvocation(activeInvocations, currentTimestamp, currentFunction);
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
                // Reuse memory of the warm invocation instead of always using unoptimized.
                currentInvocation.setMemory(warm.getMemory());
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
