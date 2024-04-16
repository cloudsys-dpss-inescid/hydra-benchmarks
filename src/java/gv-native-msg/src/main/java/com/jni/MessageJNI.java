package com.jni;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;


public class MessageJNI {
    static {
        System.loadLibrary("nativemsg-jni");
    }

    public static native void printMessage(String message);

    public static HashMap<String, Object> main(Map<String, Object> input) {
        HashMap<String, Object> output = new HashMap<>();
        printMessage("Hello from Java!");
        return output;
    }


    public static void main(String[] args) {
        HashMap<String, Object> output = new HashMap<>();
        output = main(output);
    }
}
