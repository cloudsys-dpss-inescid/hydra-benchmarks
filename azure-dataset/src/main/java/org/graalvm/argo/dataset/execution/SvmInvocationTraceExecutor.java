package org.graalvm.argo.dataset.execution;

import java.nio.charset.StandardCharsets;

public class SvmInvocationTraceExecutor extends InvocationTraceExecutor {

    public SvmInvocationTraceExecutor(ExecutorConfiguration config) {
        super(config);
    }

    @Override
    protected void uploadFunction(String owner, String function) {
        String queryParameters = "name=" + function + "&entryPoint=" + config.functionEntryPoint +
                "&language=" + config.functionLanguage + "&sandbox=" + config.gvSandbox;
        if (!config.isDebugMode()) {
            NetworkUtils.sendPost(config.getProxyAddress(), "/register?" + queryParameters, "application/octet-stream", config.functionCode, -1, false);
        }
    }

    @Override
    protected void invokeFunction(String owner, String function, int allocatedMemoryMb, int duration, int timestamp) {
        String dataString = "{\"name\":\"" + function + "\",\"async\":\"false\",\"cached\":\"" + config.gvCache + "\",\"arguments\":\"{}\"}";
        byte[] data = dataString.getBytes(StandardCharsets.UTF_8);
        if (config.isDebugMode()) {
            System.out.println("Sending request with timestamp: " + timestamp);
        } else {
            NetworkUtils.sendPost(config.getProxyAddress(), "/", "application/json; charset=UTF-8", data, timestamp, true);
        }
    }
}
