package org.graalvm.argo.dataset.execution;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class NetworkUtils {

    private static final Pattern pattern = Pattern.compile("process time \\(us\\)\":(\\d+)");

    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(30)).build();

    public static void sendPost(String address, String path, String contentType, byte[] content, int timestamp, boolean async) {
        HttpRequest request = HttpRequest.newBuilder(URI.create("http://" + address + path))
                .timeout(Duration.ofMinutes(3))
                .header("Content-Type", contentType)
                .header("accept", "application/json; charset=UTF-8")
                .POST(HttpRequest.BodyPublishers.ofByteArray(content)).build();

        if (async) {
            HTTP_CLIENT.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                    .thenApply(HttpResponse::body)
                    .thenAccept(r -> acceptRequestResult(timestamp, r));
        } else {
            try {
                HttpResponse<String> response = HTTP_CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
                System.out.println(response.body());
            } catch (IOException | InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

     public static void acceptRequestResult(int timestamp, String result) {
        System.out.println(result);
         Matcher matcher = pattern.matcher(result);
         if (matcher.find()) {
             InvocationTraceExecutor.latencies.add(timestamp + " " + matcher.group(1));
         }
     }
}
