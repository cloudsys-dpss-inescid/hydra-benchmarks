package com.dbreader;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.Socket;
import java.net.URL;
import java.net.URLConnection;
import java.util.Map;
import java.util.HashMap;
import org.graalvm.nativeimage.c.function.CEntryPoint;
import org.graalvm.nativeimage.IsolateThread;



// ./benchmark-graalvisor.sh svm gv_java_hw test 1
// ./benchmark-graalvisor.sh svm gv_java_httprequest test 1
// ./benchmark-graalvisor.sh svm gv_java_dbreader test 1
public class DBReader {
    
    static String keyObject = "foo";
    static String serverIP = "127.0.0.1";
    static String serverPort = "11211";
    static Socket socket = null;

    /* Read some key from Memcached */
    public static HashMap<String, Object> singleKeyRrequest(String key, String serverIP, int serverPort) {
        
        HashMap<String, Object> output = new HashMap<>();
        
        try {
            // Connect to Memcached server
            if(socket == null)
                socket = new Socket(serverIP, serverPort);
                socket.setSoTimeout(10000);

            // Send the "get" command for the "foo" key
            String request = "get " + key + "\r\n";
            socket.getOutputStream().write( request.getBytes());
            socket.getOutputStream().flush();

            // Read response from the server
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String line;
            int received_lines = 0; 
            while ((line = reader.readLine()) != null) {
                
                if (line.equals("END") && received_lines == 0) {  // in memcached if first line is not END, then it should be "ok"
                    System.out.println("Received END, key may no exist.");
                    break;
                }

                if (line.equals("END")) {//memcached does not close the connection, so we find "end" and exit
                    break;
                }


                // receive response from memchacher, the first line is metadata and the second e the value of the key
                received_lines++;

                if(received_lines == 1){
                    output.put("metadata", line);
                }else if(received_lines == 2){
                    output.put("value", line);
                }


            }

            // Close the socket
            // socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }


        return output;
    }


    /* For Graalvisor invocation. */
    public static HashMap<String, Object> main(Map<String, Object> args) {
        HashMap<String, Object> output = new HashMap<>();
        output = singleKeyRrequest( (String)args.get("key"), (String)args.get("serverIP"),  Integer.parseInt((String) args.get("serverPort")) );
        
        int size = output.size();
        output.put("size", size );

        return output;
    }

    /* For standalone invocations. */
    public static void main(String[] args) {
        HashMap<String, Object> output = new HashMap<>();

        output.put("key", keyObject); 
        output.put("serverIP", serverIP);
        output.put("serverPort", serverPort);      

        output = main(output);
        System.out.println(output);
    }

    /* For c-API invocations. */
    @CEntryPoint(name = "entrypoint")
    public static void main(IsolateThread thread) {
        HashMap<String, Object> output = new HashMap<>();

        output.put("key", keyObject); // TODO - receive arg.
        output.put("serverIP", serverIP);
        output.put("serverPort", serverPort);      

        output = main(output);
        System.out.println(output);
    }
}
