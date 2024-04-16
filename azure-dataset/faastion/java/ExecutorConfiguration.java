
public class ExecutorConfiguration {

    final byte[] functionCode;
    final int numFunctions;
    final String functionEntryPoint;
    final String gvSandbox;
    /**
     * If true, then print timestamps instead of issuing requests.
     */
    private final boolean debug;
    private final String lambdaManagerAddress;

    ExecutorConfiguration(byte[] functionCode, String functionEntryPoint, int numFunctions, String gvSandbox, boolean debug, String lambdaManagerAddress) {
        this.functionCode = functionCode;
        this.functionEntryPoint = functionEntryPoint;
        this.numFunctions = numFunctions;
        this.gvSandbox = gvSandbox;
        this.debug = debug;
        this.lambdaManagerAddress = lambdaManagerAddress;
    }

    public boolean isDebugMode() {
        return debug;
    }

    public String getLambdaManagerAddress() {
        return lambdaManagerAddress;
    }

}
