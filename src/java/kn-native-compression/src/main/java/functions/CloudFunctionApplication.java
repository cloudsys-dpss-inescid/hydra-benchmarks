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

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.Map;
import java.util.HashMap;

import java.util.concurrent.ThreadLocalRandom;

@SpringBootApplication
public class CloudFunctionApplication {

  public static String IMG_FILENAME = String.format("img-%d.png", ThreadLocalRandom.current().nextInt(0, 1024 + 1));
    
  private static boolean loaded = false;
  
  public static native void compress(String filePath);

  public static void main(String[] args) {
    try {
      System.load("/native-image/libzip-jni.so");
      loaded = true;
    } catch (Throwable t) {}
    SpringApplication.run(CloudFunctionApplication.class, args);
  }

  public static boolean downloadFile(String url, String filePath) {
    InputStream is = null;
    FileOutputStream fos = null;
    try {
      URLConnection conn = new URL(url).openConnection();
      is = conn.getInputStream();
      fos = new FileOutputStream(filePath);

      byte[] buffer = new byte[4096];
      int bytesRead;
      while ((bytesRead = is.read(buffer)) != -1) {
        fos.write(buffer, 0, bytesRead);
      }
        return true;
    } catch (IOException e) {
      e.printStackTrace();
      return false;
    } finally {
      try {
        if (is != null) is.close();
        if (fos != null) fos.close();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
  }

  @Bean
  public Function<Message<Map<String, Object>>, String> echo() {
    return (inputMessage) -> {
      String output = "";
      long start = System.nanoTime();
      try {
        long threadId = Thread.currentThread().getId();
        String tmpDir = "/tmp/sandbox-" + threadId;
        initTmpDirectory(tmpDir);

        Map<String, Object> payload = inputMessage.getPayload();
        String filePath = tmpDir + "/" + IMG_FILENAME;
        String url = (String)payload.get("url");

        if (loaded == false) {
          return "zip-jni not found";
        }

        boolean success;
        if ((success = downloadFile(url, filePath))) {
          compress(filePath);
        }

        output = String.valueOf(success);
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

  public static void initTmpDirectory(String directoryPath) {
    Path path = Paths.get(directoryPath);
    if (Files.notExists(path)) {
      try {
        Files.createDirectories(path);
      } catch (IOException e) {
        System.err.println(String.format("[thread %d] Error creating %s directory: %s", Thread.currentThread().getId(), directoryPath, e.getMessage()));
      }
    }
  }
  
}
