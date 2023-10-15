package com.jni;

import java.util.HashMap;
import java.util.Map;


public class HelloJNI {
    static {
        System.loadLibrary("hello");
    }

    public static native void printHello();

    public static HashMap<String, Object> main(Map<String, Object> input) {
        HashMap<String, Object> output = new HashMap<>();
        printHello();
        return output;
    }


    public static void main(String[] args) {
        HashMap<String, Object> output = new HashMap<>();
        output = main(output);
    }
}
