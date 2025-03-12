package com.hello_world;

import java.io.IOException;
import java.util.Map;

import com.oracle.graalos.WebServerMain;
import com.oracle.graalos.workload.Workload;
import com.hello_world.HelloWorld;

public class GraalHostMain {

    public static void main(String[] args) {
        try {
            WebServerMain.main(new BenchmarkWorkload());
        } catch (IOException e) {
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }

    private static class BenchmarkWorkload implements Workload {

        @Override
        public Map<String, Object> invoke(Map<String, Object> args) {
            return HelloWorld.main(args);
        }
    }
}
