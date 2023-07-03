package org.graalvm.argo.dataset.aot;

import org.graalvm.argo.dataset.Invocation;

public class AOTInvocation extends Invocation {

    private boolean optimized;
    private static final double OPTIMIZED_FOOTPRINT_RATIO = 0.375;

    public AOTInvocation(String owner, String function, int memory, int duration, int timestamp) {
        super(owner, function, memory, duration, timestamp);
        this.optimized = false;
    }

    public void setMemory(int memory) {
        this.memory = memory;
    }

    public void optimize() {
        assert optimized == false;
        memory = (int) ((double) memory * OPTIMIZED_FOOTPRINT_RATIO);
        optimized = true;
    }

    public boolean isOptimized() {
        return optimized;
    }
}
