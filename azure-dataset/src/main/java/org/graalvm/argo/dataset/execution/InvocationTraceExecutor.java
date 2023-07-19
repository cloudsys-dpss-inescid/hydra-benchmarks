package org.graalvm.argo.dataset.execution;

import org.graalvm.argo.dataset.InvocationTraceGenerator;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;

public class InvocationTraceExecutor {

    private final ExecutorConfiguration config;

    public InvocationTraceExecutor(ExecutorConfiguration config) {
        this.config = config;
    }

    // HashOwner,HashFunction,AverageAllocatedMb,AverageDuration,Timestamp
    public void execute(String invocationsFilePath) {
        Set<String> uploadedFunctions = new HashSet<>();
        try (BufferedReader br = new BufferedReader(new FileReader(invocationsFilePath))) {
            String line;
            String[] splitRow;
            br.readLine(); // To skip the header
            int currentTimestamp = 0;
            while ((line = br.readLine()) != null) {
                splitRow = line.split(InvocationTraceGenerator.DELIMITER);
                String owner = splitRow[0];
                String function = splitRow[1];
                int allocatedMemoryMb = Integer.valueOf(splitRow[2]);
                int duration = Integer.valueOf(splitRow[3]);
                int timestamp = Integer.valueOf(splitRow[4]);

                if (!uploadedFunctions.contains(function)) {
                    uploadFunction(owner, function);
                    uploadedFunctions.add(function);
                }

                int timeToSleep = (timestamp - currentTimestamp) % 3600000;
                int memoryToAllocate = (int) (allocatedMemoryMb * 1024 * 1024 * 0.05);
                currentTimestamp = timestamp;
                if (timeToSleep != 0) {
                    try {
                        Thread.sleep(timeToSleep);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }

                byte[] data = ("{\"memory\":\"" + memoryToAllocate + "\",\"duration\":\"" + duration + "\"}").getBytes(StandardCharsets.UTF_8);
                if (config.isDebugMode()) {
                    System.out.println("Sending request with timestamp: " + timestamp);
                } else {
                    NetworkUtils.sendPost(config.getLambdaManagerAddress(), "/" + owner + "/" + function, "application/json; charset=UTF-8", data, true);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        // Sleep for 1 min to wait for all async requests to complete.
        try {
            Thread.sleep(60000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    private void uploadFunction(String owner, String function) {
        String queryParameters = "username=" + owner + "&function_name=" + function +
                "&function_language=" + config.functionLanguage + "&function_entry_point=" + config.functionEntryPoint +
                "&function_memory=" + config.functionMemory + "&function_runtime=" + config.functionRuntime +
                "&function_isolation=" + config.functionIsolation + "&invocation_collocation=" + config.invocationCollocation;
        if (config.gvSandbox != null) {
            queryParameters = queryParameters + "&gv_sandbox=" + config.gvSandbox;
        }
        if (!config.isDebugMode()) {
            NetworkUtils.sendPost(config.getLambdaManagerAddress(), "/upload_function?" + queryParameters, "application/octet-stream", config.functionCode, false);
        }
    }

}
