import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class InvocationTraceExecutor {

    private static final int MS_IN_HOUR = 3600000;
    private static final int BYTES_IN_MB = 1048576;
    /**
     * Empirical value used to calculate request-specific memory consumption.
     */
    private static final double MEMORY_COEFFICIENT = 0.05;

    private final ExecutorConfiguration config;

    public static Map<Integer, String> hashMap = Map.of(
            0, "gv_native_hw");

    public InvocationTraceExecutor(ExecutorConfiguration config) {
        this.config = config;
    }

    // HashOwner,HashFunction,AverageAllocatedMb,AverageDuration,Timestamp
    public void execute(String invocationsFilePath) {
        uploadFunctions(invocationsFilePath);
        try (BufferedReader br = new BufferedReader(new FileReader(invocationsFilePath))) {
            String line;
            String[] splitRow;
            br.readLine(); // To skip the header
            int currentTimestamp = 0;
            while ((line = br.readLine()) != null) {
                splitRow = line.split(",");

                int function = Integer.valueOf(splitRow[0]);
                int timestamp = Integer.valueOf(splitRow[1]);

                waitForInvocation(currentTimestamp, timestamp);
                currentTimestamp = timestamp;
                invokeFunction(hashMap.get(function), timestamp);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void uploadFunctions(String invocationsFilePath) {
        Set<String> uploadedFunctions = new HashSet<>();
        try (BufferedReader br = new BufferedReader(new FileReader(invocationsFilePath))) {
            String line;
            String[] splitRow;
            br.readLine(); // To skip the header
            while ((line = br.readLine()) != null) {
                splitRow = line.split(",");
                int function = Integer.parseInt(splitRow[0]);
                ensureUploaded(uploadedFunctions, hashMap.get(function));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void ensureUploaded(Set<String> uploadedFunctions, String function) {
        if (!uploadedFunctions.contains(function)) {
            uploadFunction(function);
            uploadedFunctions.add(function);
        }
    }

    private void waitForInvocation(int currentTimestamp, int invocationTimestamp) {
        int timeToSleep = (invocationTimestamp - currentTimestamp) % MS_IN_HOUR;
        if (timeToSleep != 0) {
            try {
                Thread.sleep(timeToSleep);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void uploadFunction(String function) {
        String queryParameters = "name=" + function + "&language=java&entryPoint=" + config.functionEntryPoint;
        NetworkUtils.sendPost(config.getLambdaManagerAddress(), "/register?" + queryParameters,
                "application/octet-stream", config.functionCode, false);
    }

    private void invokeFunction(String function, int timestamp) {
        byte[] data = ("{\"name\":\"" + function + "\",\"async\":\"false\",\"cached\":\"true\",\"arguments\":\"\"}").getBytes(StandardCharsets.UTF_8);
        if (config.isDebugMode()) {
            System.out.println("Sending request with timestamp: " + timestamp);
        }
        NetworkUtils.sendPost(config.getLambdaManagerAddress(), "/" + function, "application/json; charset=UTF-8", data, true);
     }
}
