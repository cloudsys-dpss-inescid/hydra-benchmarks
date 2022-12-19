package com.odd_even;

import java.util.HashMap;
import java.util.Map;

@SuppressWarnings("unused")
public class OddEven {

    static Map<String, Object> output = new HashMap<>();

    public static Map<String, Object> main(Map<String, Object> input) {
        int num = Integer.parseInt((String)input.get("number"));

        if (num % 2 == 0) {
            output.put("number", "even");
            System.exit(0);
        }
        else {
            output.put("number", "odd");
        }

        return output;
    }

}
