package com.fibonnaci;

import java.util.HashMap;
import java.util.Map;


@SuppressWarnings("unused")
public class Fibonnaci {

    public static HashMap<String, Object> main(Map<String, Object> input) {
        HashMap<String, Object> output = new HashMap<>();
        int term = Integer.parseInt((String)input.get("term"));
        output.put("fibonnaci", fibonacci(term));
        return output;
    }

    private static String fibonacci(int term) {
        if (term == 1 || term == 2) {
            return "1";
        }
        int f1 = 1, f2 = 1, t = 2;
        while (t != term) {
            int new_term = f1 + f2;
            f1 = f2;
            f2 = new_term;
            t++;
        }
        return String.valueOf(f2);
    }

    public static void main(String[] args) {
        HashMap<String, Object> output = new HashMap<>();
        output.put("term", "10");
        output = main(output);
        System.out.println(output);
    }
}
