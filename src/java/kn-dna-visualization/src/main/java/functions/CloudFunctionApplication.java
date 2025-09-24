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

import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import java.lang.RuntimeException;
import java.util.stream.DoubleStream;
import java.util.stream.Collectors;

import java.nio.file.Files;
import java.io.BufferedReader;

@SpringBootApplication
public class CloudFunctionApplication {

  private static class DNACoordinates {
    private List<Double> x;
    private List<Double> y;

    DNACoordinates() {
      x = new ArrayList();
      y = new ArrayList();
    }   

    List<Double> getHorizontalCoordinates() {
      return x;
    }

    List<Double> getVerticalCoordinates() {
      return y;
    }

    String getHorizontalCoordinates(int start, int end) {
      return x.stream().skip(start).limit(end)
              .map(d -> String.valueOf(d))
              .collect(Collectors.joining(", ", "[", "]"));            
    }

    String getVerticalCoordinates(int start, int end) {
      return y.stream().skip(start).limit(end)
              .map(d -> String.valueOf(d))
              .collect(Collectors.joining(", ", "[", "]")); 
    }

    @Override
    public String toString() {
      return x.stream().map(d -> String.valueOf(d))
              .collect(Collectors.joining(", ", "[[", "], "))
            + y.stream().map(d -> String.valueOf(d))
              .collect(Collectors.joining(", ", "[", "]]"));
    }
  }

  public static DNACoordinates transform(String sequence, String method) {
    return transform(sequence, method, false);
  }

  public static DNACoordinates transform(String sequence, boolean bar) {
    return transform(sequence, "squiggle", bar);
  }

  public static DNACoordinates transform(String sequence) {
    return transform(sequence, "squiggle", false);
  }

  public static DNACoordinates transform(String s, String method, boolean bar) {
    String sequence = s.toUpperCase();

    DNACoordinates dna = new DNACoordinates();
    List<Double> x = dna.getHorizontalCoordinates();
    List<Double> y = dna.getVerticalCoordinates();

    if (method.equals("squiggle")) {
      y.add(0.);
      for (int i = 0; i < 2 * sequence.length() + 1; i++) {
        x.add(i * 0.5);
      }

      double[] arr;
      double running_value = 0;
      for (char c : sequence.toCharArray()) {
        if (c == 'A') {
          arr = new double[] {running_value + 0.5, running_value};
        } else if (c == 'C') {
          arr = new double[] {running_value - 0.5, running_value};
        } else if (c == 'T') {
          arr = new double[] {running_value - 0.5, running_value - 1};
          running_value -= 1;
        } else if (c == 'G') {
          arr = new double[] {running_value + 0.5, running_value + 1};
          running_value += 1;
        } else {
          arr = new double[] {running_value, running_value};
        }
          y.addAll(DoubleStream.of(arr).boxed().collect(Collectors.toList()));
      }

      return dna;
    }

    else {
      throw new RuntimeException("Invalid method. Valid methods are 'squiggle', 'gates', 'yau', and 'randic'.");
    }

  }

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

  @Bean
  public Function<Message<Map<String, Object>>, String> echo() {
    return (inputMessage) -> {
      String output = "";
      long start = System.nanoTime();
      try {
        Map<String, Object> payload = inputMessage.getPayload();
        String filePath = "/tmp/bacillus_subtilis.fasta";
        String url = (String)payload.get("url");

        // String result = "Error: something went wrong";
        // if (downloadFile(url, filePath)) {
        //   try {
        //     BufferedReader reader = Files.newBufferedReader(Paths.get(filePath));
        //     String fastaSequence = reader.lines().collect(Collectors.joining());
        //     DNACoordinates dna = transform(fastaSequence);
        //     result = "(" + dna.getHorizontalCoordinates(0, 10)
        //             + ", " + dna.getVerticalCoordinates(0, 10) + ")";
        //   } catch (IOException e) {
        //     e.printStackTrace();
        //   }
        // }

        DNACoordinates dna = transform(
"ATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAG" +
"TTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTGGACCCAGAGGTTCTTTGAGTCCTTTGG" +
"GGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAGGTGAAGGCTCATGGCAAGAAAGTGCTCGGT" +
"GCCTTTAGTGATGGCCTGGCTCACCTGGACAACCTCAAGGGCACCTTTGCCACACTGAGTGAGCTGCACT" +
"GTGACAAGCTGCACGTGGATCCTGAGAACTTCAGGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCA" +
"TCACTTTGGCAAAGAATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAAT" +
"GCCCTGGCCCACAAGTATCACTAA"
        );
        String result = "(" + dna.getHorizontalCoordinates(0, 10)
                        + ", " + dna.getVerticalCoordinates(0, 10) + ")";

        output = result;
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
