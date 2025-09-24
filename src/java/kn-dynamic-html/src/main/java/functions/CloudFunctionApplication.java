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

import java.io.PrintWriter;

import com.github.mustachejava.DefaultMustacheFactory;
import com.github.mustachejava.Mustache;
import com.github.mustachejava.MustacheFactory;

import java.util.Date;
import java.util.Random;
import java.text.SimpleDateFormat;
import java.util.stream.Collectors;

@SpringBootApplication
public class CloudFunctionApplication {

  private static final int TEST_INPUT = 10;
  private static final int SMALL_INPUT = 1000;
  private static final int LARGE_INPUT = 100000;

  public static void main(String[] args) {
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

  public static boolean renderTemplate(String filePath, String name, int size) {
    MustacheFactory mf = new DefaultMustacheFactory();
    Mustache mustache = mf.compile(filePath);
    Map<String, Object> contents = new HashMap();
    contents.put("username", name);
    contents.put("cur_time", new SimpleDateFormat("MM/dd/yyyy HH:mm:ss")
            .format(new Date()));
    contents.put("random_numbers", new Random().ints(size, 0, 101)
            .mapToObj(n -> String.valueOf(n))
            .collect(Collectors.toList()));
    try {
      mustache.execute(new PrintWriter(System.out), contents).flush();
    } catch (IOException e) {
      e.printStackTrace();
      return false;
    }
    return true;
  }

  @Bean
  public Function<Message<Map<String, Object>>, String> echo() {
    return (inputMessage) -> {
      String output = "";
      long start = System.nanoTime();
      try {
        Map<String, Object> payload = inputMessage.getPayload();
        String tmpDir = "/tmp/sandbox-" + Thread.currentThread().getId();
        String filePath = tmpDir + "/template.html";
        String url = (String)payload.get("url");

        boolean success;
        initTmpDirectory(tmpDir);
        if ((success = downloadFile(url, filePath))) {
          success = renderTemplate(filePath, "testname", SMALL_INPUT);
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
