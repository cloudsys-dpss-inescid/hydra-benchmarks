package com.oracle.graalos;

import com.oracle.graalos.workload.Workload;

import java.io.IOException;


public class WebServerMain {

    public static void main(Workload workload) throws IOException {
        String lambdaPortEnv = System.getenv("lambda_port");

        int lambdaPort = 9001;
        if (lambdaPortEnv != null) {
            lambdaPort = Integer.parseInt(lambdaPortEnv);
        }

        new RuntimeProxy(lambdaPort, workload).start();
    }
}
