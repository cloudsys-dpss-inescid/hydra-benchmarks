package functions;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.messaging.Message;

import java.util.function.Function;

import java.io.File;
import java.nio.file.Files;
import java.io.FileOutputStream;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.Map;
import java.util.HashMap;

@SpringBootApplication
public class CloudFunctionApplication {
    
  private static boolean loaded = false;
  
  public static native void pagerank();

  public static void main(String[] args) {
    try {
      System.load("/native-image/libpagerank-jni.so");
      loaded = true;
    } catch (Throwable t) {}
    SpringApplication.run(CloudFunctionApplication.class, args);
  }

  @Bean
  public Function<Message<Map<String, Object>>, String> echo() {
    return (inputMessage) -> {
      String output = "";
      long start = System.nanoTime();
      try {
        Map<String, Object> payload = inputMessage.getPayload();

        if (loaded == false) {
          return "pagerank-jni not found";
        }

	      pagerank();

        output = String.valueOf(true);
      } catch (Exception e) {
        e.printStackTrace();
        output = e.getMessage();
      } finally {
        long finish = System.nanoTime();
        double processTime = (finish - start) / 1000;
        return "{result:" + output + ",process_time(us):" + processTime + "}";
      }
    };
  }
  
}
