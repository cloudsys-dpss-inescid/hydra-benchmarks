package com.filehashing;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.math.BigInteger;
import java.util.Map;
import java.util.HashMap;

public class FileHashing {

    public static HashMap<String, Object> main(Map<String, Object> args) {
        HashMap<String, Object> output = new HashMap<>();

        byte[] bytes = new byte[1000];
        Random random = new Random();
        random.nextBytes(bytes);
		
		try {
			output.put("hash", String.format("%032X", new BigInteger(1, MessageDigest.getInstance("MD5").digest(bytes))));
		} catch (NoSuchAlgorithmException e) {
			output.put("hash", e.getMessage());
			e.printStackTrace();
		}

        return output;
    }

    public static void main(String[] args) {
    	HashMap<String, Object> output = new HashMap<>();
    	output = main(output);
    }
}
