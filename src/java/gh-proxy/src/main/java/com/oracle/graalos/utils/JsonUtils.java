package com.oracle.graalos.utils;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.jr.ob.JSON;

public class JsonUtils {

    private static final JSON json = JSON.std;
    private final static ObjectMapper mapper = new ObjectMapper();

    /**
     * Extract arguments json encoded string into Map.
     *
     * @param jsonString json encoded String
     * @return map that illustrates json
     */
    public static Map<String, Object> jsonToMap(String jsonString) {
        try {
            if (jsonString != null && jsonString.length() > 0) {
                return json.mapFrom(jsonString);
            }
        } catch (IOException e) {
            e.printStackTrace(System.err);
        }
        return new HashMap<>();
    }

    public static String mapToJson(Map<String, Object> jsonObject) {
        try {
            return mapper.writeValueAsString(jsonObject);
        } catch (JsonProcessingException e) {
            e.printStackTrace(System.err);
        }
        return "";
    }
}
