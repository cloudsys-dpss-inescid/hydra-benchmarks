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

    @Override
    public String toString() {
        String baseOutput = super.toString();
        return String.format("%s | optimized_cold %s running_optimized_functions %s", baseOutput, optimizedColdStarts, runningOptimizedFunctions);
    }
}
