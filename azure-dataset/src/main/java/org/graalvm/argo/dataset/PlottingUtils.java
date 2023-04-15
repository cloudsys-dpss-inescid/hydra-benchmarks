package org.graalvm.argo.dataset;

import java.nio.file.Paths;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

public class PlottingUtils {

    private static final String AGGREGATED_INVOCATION_DATA = "%d %d %d %d %d %d %d %d";

    public static void printTraceSimulation(List<Invocation> invocations, String filename, int keepAlive) {
        simulateTrace(invocations, filename, keepAlive);
    }

    private static void simulateTrace(List<Invocation> invocations, String filename, int keepAlive) {
        Set<Invocation> activeInvocations = new HashSet<>();
        List<String> aggregatedInvocationData = new LinkedList<>();
        System.out.println("Simulating trace with " + invocations.size() + " invocations");
        int invocationsProcessed = 0;

        for (Invocation currentInvocation : invocations) {
            int currentInvocationTimestamp = currentInvocation.getTimestamp();
            activeInvocations.removeIf(f -> currentInvocationTimestamp >= f.getEndTimestamp() + keepAlive);
            activeInvocations.add(currentInvocation);
            /* gather aggregated invocation data for plot */
            long activeUsers = activeInvocations.stream().filter(i -> i.getEndTimestamp() > currentInvocationTimestamp).map(Invocation::getOwner).distinct().count();
            long activeFunctions  = activeInvocations.stream().filter(i -> i.getEndTimestamp() > currentInvocationTimestamp).map(Invocation::getFunction).distinct().count();
            long cachedActiveUsers = activeInvocations.parallelStream().map(Invocation::getOwner).distinct().count();
            long cachedActiveFunctions = activeInvocations.parallelStream().map(Invocation::getFunction).distinct().count();
            long runningInvocations = activeInvocations.stream().filter(i -> i.getEndTimestamp() > currentInvocationTimestamp).count();
            long runningInvocationsFootprint = activeInvocations.stream().filter(i -> i.getEndTimestamp() > currentInvocationTimestamp).mapToInt(Invocation::getMemory).sum();
            long cachedFunctionsFootprint = activeInvocations.stream().mapToInt(Invocation::getMemory).sum();
            // TODO - why not writing to disk directly? This will accumulate more and more memory.
            aggregatedInvocationData.add(String.format(AGGREGATED_INVOCATION_DATA, currentInvocationTimestamp, activeUsers, activeFunctions, cachedActiveUsers, cachedActiveFunctions, runningInvocations, runningInvocationsFootprint, cachedFunctionsFootprint));
            if (invocationsProcessed % 10000 == 0) {
                System.out.println(invocationsProcessed);
            }
            ++invocationsProcessed;
        }
        DatasetProcessor.writeToFile(aggregatedInvocationData, Paths.get("output", filename));
    }
}
