package com.example.spring.demo.svg;

import org.eclipse.rdf4j.repository.RepositoryConnection;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class Main {


  public void execute(List<String> variablesToColor, List<String> schermate) throws IOException {

    File f1 = new File("./ontologies/saref4bldg-solo-classi-e-proprieta.owl");
    File f2 = new File("./ontologies/saref4bldg-ext-toTEMP.owl");


    File theDir = new File("./directory");


    if (!theDir.exists()) {
      theDir.mkdirs();
    }

    //// se la directory per qualche motivo ha dei file dentro.....vengono eliminati.... altrimenti può generare errori
    if (theDir.isDirectory() && theDir.list().length != 0) {
      File[] listOfFiless = theDir.listFiles();
      for (File f : listOfFiless) {
        f.delete();
      }
    }

    List<String> csv_paths = new ArrayList<>();

    for (String s : schermate)
      csv_paths.add(s);


    for (String s : csv_paths) {
      Files.copy(Path.of("./all_csv/" + s), Path.of("./directory/" + s));
    }


    AsyncExecutionFolder start = new AsyncExecutionFolder("./directory", "./ontologies/saref4bldg-solo-classi-e-proprieta.owl", variablesToColor);

    //Delete Ontologies not needed
    start.run();
    File conIndividuals = new File("./ontologies/con_individuals.owl");
    conIndividuals.delete();
    Files.copy(f1.toPath(), Path.of("./ontologies/con_individuals.owl"));
    f1.delete();
    Files.copy(f2.toPath(), Path.of("./ontologies/saref4bldg-solo-classi-e-proprieta.owl")); // in questa maniera se pur i dati vengono copiati nell'ontologia questa viene resettata per automaatizzare il processo ricorsivamnete
    // delete CSVs
    File folder = new File("./directory/");
    File[] listOfFiles = folder.listFiles();
    for (File f : listOfFiles) {
      f.delete();
    }


    File ontologyFile = new File("./ontologies/con_individuals.owl");

    RepositoryConnection repCon = UpdateOntologyFiletoRepository.getRepositoryConnection();
    UpdateOntologyFiletoRepository.deleteEverythingFromRepository(repCon);
    UpdateOntologyFiletoRepository.uploadOntology(repCon, ontologyFile);

  }




  public static void main(String[] args) throws Exception {


    //// prove
    Main main = new Main();
    List l = new ArrayList();
    l.add("s-904a");
    List schermate = new ArrayList();
    schermate.add("CARICO_FERRICO_FERROSO.csv");
    main.execute(l, schermate);


  }
}
