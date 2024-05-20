package com.sleep;

import java.lang.InterruptedException;
import java.util.HashMap;
import java.util.Map;


@SuppressWarnings("unused")
public class Sleep {

    static Map<String, Object> output = new HashMap<>();

    static byte[] buffer;

    public static void memory(int bytes) {
        buffer = new byte[bytes];
        for (int i = 0; i < bytes; i++) {
            buffer[i] = 1;
        }
    }

    public static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ie) {
            output.put("Log", "InterruptedException");
        }
    }

    public static Map<String, Object> main(Map<String, Object> input) {
        memory(1024);
        sleep(1000);
        return output;
    }

    public static void main(String[] args) {
        Map<String, Object> output = new HashMap<>();
        output = main(output);
    }

}
