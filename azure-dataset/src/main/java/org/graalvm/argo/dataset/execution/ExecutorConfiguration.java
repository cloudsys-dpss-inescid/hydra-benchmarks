package org.graalvm.argo.dataset.execution;

public class ExecutorConfiguration {

    final byte[] functionCode;
    final String functionLanguage;
    final String functionEntryPoint;
    final String functionMemory;
    final String functionRuntime;
    final String invocationCollocation;
    final String functionIsolation;
    final String gvSandbox;
    final String gvCache;
    /**
     * If true, then print timestamps instead of issuing requests.
     */
    private final boolean debug;
    private final String proxyAddress;

    ExecutorConfiguration(byte[] functionCode, String functionLanguage, String functionEntryPoint, String functionMemory, String functionRuntime, String invocationCollocation, String functionIsolation, String gvSandbox, boolean debug, String lambdaManagerAddress) {
        this.functionCode = functionCode;
        this.functionLanguage = functionLanguage;
        this.functionEntryPoint = functionEntryPoint;
        this.functionMemory = functionMemory;
        this.functionRuntime = functionRuntime;
        this.invocationCollocation = invocationCollocation;
        this.functionIsolation = functionIsolation;
        this.gvSandbox = gvSandbox;
        this.gvCache = null;
        this.debug = debug;
        this.proxyAddress = lambdaManagerAddress;
    }

    ExecutorConfiguration(byte[] functionCode, String functionLanguage, String functionEntryPoint, String gvSandbox, String gvCache, boolean debug, String gvProxyAddress) {
        this.functionCode = functionCode;
        this.functionLanguage = functionLanguage;
        this.functionEntryPoint = functionEntryPoint;
        this.functionMemory = null;
        this.functionRuntime = null;
        this.invocationCollocation = null;
        this.functionIsolation = null;
        this.gvSandbox = gvSandbox;
        this.gvCache = gvCache;
        this.debug = debug;
        this.proxyAddress = gvProxyAddress;
    }

    public boolean isDebugMode() {
        return debug;
    }

    public String getProxyAddress() {
        return proxyAddress;
    }

}
