package com.oracle.graalos;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.Map;

import com.oracle.graalos.utils.HttpUtils;
import com.oracle.graalos.workload.Workload;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import static com.oracle.graalos.utils.HttpUtils.errorResponse;
import static com.oracle.graalos.utils.HttpUtils.writeResponse;
import static com.oracle.graalos.utils.JsonUtils.jsonToMap;
import static com.oracle.graalos.utils.JsonUtils.mapToJson;


public class RuntimeProxy {

    interface ProxyHttpHandler extends HttpHandler {

        void handleInternal(HttpExchange exchange) throws IOException;

        @Override
        default void handle(HttpExchange he) throws IOException {
            try {
                // Handling CORS
                he.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
                if (he.getRequestMethod().equalsIgnoreCase("OPTIONS")) {
                    he.getResponseHeaders().add("Access-Control-Allow-Methods", "GET, OPTIONS");
                    he.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type,Authorization");
                    he.sendResponseHeaders(204, -1);
                    return;
                }
                handleInternal(he);
            } catch (Exception e) {
                e.printStackTrace(System.err);
                errorResponse(he, "An error has occurred (see logs for details): " + e);
            }
        }
    }

    private final Workload workload;
    private final HttpServer server;

    public RuntimeProxy(int port, Workload workload) throws IOException {
        this.workload = workload;
        server = HttpServer.create(new InetSocketAddress(port), 0);
        server.setExecutor(java.util.concurrent.Executors.newSingleThreadExecutor());
        server.createContext("/invoke", new InvocationHandler());
    }

    public void start() {
        server.start();
    }

    private class InvocationHandler implements ProxyHttpHandler {

        @Override
        public void handleInternal(HttpExchange t) throws IOException {
            Map<String, Object> input = jsonToMap(HttpUtils.extractRequestBody(t));
            Map<String, Object> result = workload.invoke(input);
            writeResponse(t, 200, mapToJson(result));
        }
    }
}
