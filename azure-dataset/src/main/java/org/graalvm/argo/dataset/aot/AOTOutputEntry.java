package org.graalvm.argo.dataset.aot;

import org.graalvm.argo.dataset.OutputEntry;

public class AOTOutputEntry extends OutputEntry {

    protected int optimizedColdStarts;
    protected int runningOptimizedFunctions;

    public AOTOutputEntry(
            int timestamp,
            int invocationsProcessed,
            int coldStarts,
            int optimizedColdStarts,
            int runningUsers,
            int runningFunctions,
            int runningOptimizedFunctions,
            int runningInvocations,
            int runningInvocationsFootprint,
            int cachedUsers,
            int cachedFunctions,
            int cachedInvocationsFootprint) {
        super(timestamp, invocationsProcessed, coldStarts, runningUsers, runningFunctions, runningInvocations, runningInvocationsFootprint, cachedUsers, cachedFunctions, cachedInvocationsFootprint);
        this.optimizedColdStarts = optimizedColdStarts;
        this.runningOptimizedFunctions = runningOptimizedFunctions;
    }

    public static String toString(
            int timestamp,
            int invocationsProcessed,
            int coldStarts,
            int optimizedColdStarts,
            int runningUsers,
            int runningFunctions,
            int runningOptimizedFunctions,
            int runningInvocations,
            int runningInvocationsFootprint,
            int cachedUsers,
            int cachedFunctions,
            int cachedInvocationsFootprint) {
        return String.format("time %s | invocations %s cold %s optimized_cold %s | running users %s functions %s optimized_functions %s invocations %s footprint %s | cached users %s functions %s footprint %s",
                timestamp, invocationsProcessed, coldStarts, optimizedColdStarts, runningUsers, runningFunctions, runningOptimizedFunctions, runningInvocations, runningInvocationsFootprint, cachedUsers, cachedFunctions, cachedInvocationsFootprint);
    }

    @Override
    public String toString() {
        return toString(timestamp, invocationsProcessed, coldStarts, optimizedColdStarts, runningUsers, runningFunctions, runningOptimizedFunctions, runningInvocations, runningInvocationsFootprint, cachedUsers, cachedFunctions, cachedInvocationsFootprint);
    }
}
