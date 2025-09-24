package functions;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.messaging.Message;

import java.util.function.Function;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.io.IOException;
import java.io.InputStream;
import java.io.FileOutputStream;
import java.io.ByteArrayOutputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.Map;
import java.util.HashMap;

import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.core.Core;
import org.opencv.core.Size;
import nu.pattern.OpenCV;

import java.util.concurrent.ThreadLocalRandom;

@SpringBootApplication
public class CloudFunctionApplication {

  public static String IMG_FILENAME = String.format("img-%d.png", ThreadLocalRandom.current().nextInt(0, 1024 + 1));

    public static boolean resize(String filePath, double ratio, String outFile) {
      nu.pattern.OpenCV.loadLocally();
		  Mat image = Imgcodecs.imread(filePath);
		  Imgproc.resize(image, image, new Size(0, 0), ratio, ratio);
		  Imgcodecs.imwrite(outFile, image);
      return true;
    }

    public static byte[] fromInputStream(InputStream is) throws Exception {
      ByteArrayOutputStream buffer = new ByteArrayOutputStream();
      int nRead;
      byte[] data = new byte[16384];

      while ((nRead = is.read(data, 0, data.length)) != -1) {
        buffer.write(data, 0, nRead);
      }

      return buffer.toByteArray();
    }

    public static byte[] downloadBytes(String url) {
      try {
        URLConnection conn = new URL(url).openConnection();
        InputStream is = conn.getInputStream();
        byte[] bytes = fromInputStream(is); 
        is.close();
        return bytes;
      } catch (Exception e) {
        e.printStackTrace();
        return null;
      }
    }

  public static void main(String[] args) {
    SpringApplication.run(CloudFunctionApplication.class, args);
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
        String url = (String)payload.get("url");
        String filePath = tmpDir + "/" + IMG_FILENAME;
        String outFile = tmpDir + "/output.png"; 

        boolean success = false;
        try {
          FileOutputStream stream = new FileOutputStream(filePath);
          stream.write(downloadBytes(url));
          success = resize(filePath, 0.25, outFile);
        } catch (IOException e) {
          e.printStackTrace();
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
