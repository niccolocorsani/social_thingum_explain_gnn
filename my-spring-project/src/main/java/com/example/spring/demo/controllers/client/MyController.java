package com.example.spring.demo.controllers.client;

import com.example.spring.demo.svg.Main;

import org.apache.commons.io.FileUtils;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;


import javax.swing.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;
import java.util.List;

@CrossOrigin
@RestController
@RequestMapping("/svg")
public class MyController {


  @GetMapping("/get")
  //http://localhost:8080/spring-app/svg/get?values=abc,2,3
  public String getSVG(@RequestParam List<String> values, @RequestParam List<String> schermate) throws IOException {

    Main main = new Main();
    List<String> variablesToColor = values;
    main.execute(variablesToColor, schermate);
    System.out.println("SVG.....");
    String svg = Files.readString(Path.of("./generated_svg/" + this.getLastSvgGenerated()));
    return svg;

  }


  @RequestMapping(value = "/svg-download", method = RequestMethod.GET)
  @ResponseBody
  public ResponseEntity<byte[]> downloadSVG() throws IOException {

    String content = Files.readString(Path.of("./generated_svg/" + this.getLastSvgGenerated()));
    HttpHeaders httpHeaders = new HttpHeaders();
    httpHeaders.set(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_OCTET_STREAM_VALUE); // (3) Content-Type: application/octet-stream
    httpHeaders.set(HttpHeaders.CONTENT_DISPOSITION, ContentDisposition.attachment().filename("union.svg").build().toString()); // (4) Content-Disposition: attachment; filename="demo-file.txt"
    return ResponseEntity.ok().headers(httpHeaders).body(content.getBytes()); // (5) Return Response
  }

  @RequestMapping(value = "/files", method = RequestMethod.GET)
  @ResponseBody
  public ResponseEntity<byte[]> getFile() throws IOException {

    String content = Files.readString(Path.of("./ontologies/con_individuals.owl"));
    HttpHeaders httpHeaders = new HttpHeaders();
    httpHeaders.set(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_OCTET_STREAM_VALUE); // (3) Content-Type: application/octet-stream
    httpHeaders.set(HttpHeaders.CONTENT_DISPOSITION, ContentDisposition.attachment().filename("ontology.owl").build().toString()); // (4) Content-Disposition: attachment; filename="demo-file.txt"
    return ResponseEntity.ok().headers(httpHeaders).body(content.getBytes()); // (5) Return Response
  }


  @GetMapping("/update-csv")
  public String updateCSV(@RequestParam String infoToAddToCSV, @RequestParam String csvName) throws IOException {


    try {
      Files.write(Paths.get("./all_csv/" + csvName + ".csv"), (infoToAddToCSV + "\n").getBytes(), StandardOpenOption.APPEND);
    } catch (IOException e) {
      System.err.println("probelma nella scrittura");
      System.err.println(e.getMessage());
      e.printStackTrace();

    }

    return null;

  }


  @GetMapping("/delete-raw-from-csv")
  //http://localhost:8080/spring-app/svg/get?values=abc,2,3
  public String deleteRaw(@RequestParam String rawToDelete, @RequestParam String csvName) throws Exception {

    long linesPrima = Files.lines(Paths.get("./all_csv/" + csvName + ".csv")).count();


    File inputFile = null;
    File tempFile = null;
    try {
      inputFile = new File("./all_csv/" + csvName + ".csv");
      tempFile = new File("./all_csv/" + "prova" + ".csv");

      BufferedReader reader = new BufferedReader(new FileReader(inputFile));
      BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile));

      String lineToRemove = rawToDelete;
      String currentLine;

      while ((currentLine = reader.readLine()) != null) {
        if (currentLine.equals(lineToRemove)) continue;
        writer.write(currentLine + System.getProperty("line.separator"));
      }
      writer.close();
      reader.close();
      boolean successful = tempFile.renameTo(inputFile);
      System.out.println(successful);

    } catch (Exception e) {
      e.printStackTrace();
    }


    long linesDopo = Files.lines(Paths.get("./all_csv/" + csvName + ".csv")).count();


    System.out.println("Righe prima" + linesPrima);
    System.out.println("Righe dopo" + linesDopo);
    System.setProperty("java.awt.headless", "false");

    if (linesPrima != (linesDopo + 1)) {
      JFrame frame = new JFrame("Errore");
      JOptionPane.showMessageDialog(frame, "Errore");
      throw new Exception("Errore elimina");
    }


    boolean successful = tempFile.renameTo(inputFile);


    return null;

  }


  public String getLastSvgGenerated() {
    File folder = new File("./generated_svg/");
    File[] listOfFiles = folder.listFiles();
    Map<String, Long> fileName_DateMap = new TreeMap();
    for (File f : listOfFiles) {
      fileName_DateMap.put(f.getName(), f.lastModified());
    }
    String key = Collections.max(fileName_DateMap.entrySet(), Map.Entry.comparingByValue()).getKey();
    return key;
  }


  @ExceptionHandler(value = Exception.class)
  public ResponseEntity<String> handleNullPointerException(Exception e) {
    String error = "";
    error = e.getMessage();
    System.err.println(e.getMessage());
    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    return new ResponseEntity<>(error, status);
  }

}
