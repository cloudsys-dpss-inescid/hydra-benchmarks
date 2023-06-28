package org.graalvm.argo.dataset;

import java.util.Comparator;

public class Invocation {
    // Function owner identifier.
    private final String owner;
    // Function identifier.
    private final String function;
    // Memory footprint in MBs.
    private int memory;
    // Function execution time in ms.
    private final int duration;
    // Function start timestamp in ms.
    private final int timestamp;
    // Function finish timestamp in ms.
    private final int endTimestamp;

    private boolean optimized;
    private static final double OPTIMIZED_FOOTPRINT_RATIO = 0.375;

    public Invocation(String owner, String function, int memory, int duration, int timestamp) {
        this.owner = owner;
        this.function = function;
        this.memory = memory;
        this.duration = duration;
        this.timestamp = timestamp;
        this.endTimestamp = timestamp + duration;
        this.optimized = false;
    }

    public String getOwner() {
        return owner;
    }

    public String getFunction() {
        return function;
    }

    public int getMemory() {
        return memory;
    }

    public void setMemory(int memory) {
        this.memory = memory;
    }

    public int getDuration() {
        return duration;
    }

    public int getTimestamp() {
        return timestamp;
    }

    public int getEndTimestamp() {
        return endTimestamp;
    }

    @Override
    public String toString() {
        return String.format("%s,%s,%d,%d,%d", owner, function, memory, duration, timestamp);
    }

    public static Comparator<Invocation> comparator() {
        return new Comparator<Invocation>() {

            @Override
            public int compare(Invocation o1, Invocation o2) {
                return o1.endTimestamp - o2.endTimestamp;
            }
        };
    }

    public void optimize() {
        assert optimized == false;
        memory = (int) ((double) memory * OPTIMIZED_FOOTPRINT_RATIO);
        optimized = true;
    }
}
