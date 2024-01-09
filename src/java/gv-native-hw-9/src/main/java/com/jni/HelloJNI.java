package com.jni;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;


public class HelloJNI {
    static {
        System.loadLibrary("nativehw9-jni");
    }

    public static native void printHello9();

    public static HashMap<String, Object> main(Map<String, Object> input) {
        HashMap<String, Object> output = new HashMap<>();
        printHello9();
        return output;
    }


    public static void main(String[] args) {
        HashMap<String, Object> output = new HashMap<>();
        output = main(output);
    }
}
