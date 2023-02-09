package com.example.spring.demo.svg;


import com.github.owlcs.ontapi.OntManagers;
import org.apache.commons.io.input.BOMInputStream;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;

import java.io.*;
import java.util.List;

public class AsyncExecutionFolder extends Thread {

    private final String folderPath;
    private final String ontologyPath;
    private List<String> variablesTocolor;

    public AsyncExecutionFolder(String folderPath, String ontologyPath, List<String> variablesTocolor) {
        this.folderPath = folderPath;
        this.ontologyPath = ontologyPath;
        this.variablesTocolor = variablesTocolor;
    }


    @Override
    public void run() {
        System.out.println("--------------------Starting------------------\n");
        InputStream inputStream;

        File folder = new File(folderPath);
        String[] listOfFiles = folder.list();


        for (int i = 0; i < listOfFiles.length; i++) {

            if (listOfFiles[i].equals(".DS_Store")) {
                continue;
            }
            try {
                inputStream = new FileInputStream(folderPath + '/' + listOfFiles[i]);
                System.out.println(folderPath + '/' + listOfFiles[i]);

            } catch (FileNotFoundException fileNotFoundException) {
                System.err.println("Problem with folder!\n");
                return;
            }

            System.out.println("Parsing CSV....\n");

            BOMInputStream bOMInputStream = new BOMInputStream(inputStream);
            InputStreamReader reader = new InputStreamReader(new BufferedInputStream(bOMInputStream));
            BufferedReader br = new BufferedReader(reader);

            OWLOntologyManager man = OntManagers.createONT();
            File file = new File(ontologyPath);
            OWLOntology o;

            System.out.println("Loading Ontology...\n");

            try {
                o = man.loadOntologyFromOntologyDocument(file);
            } catch (OWLOntologyCreationException e) {
                System.err.println("Invalid OWL File!\n");
                return;
            }

            System.out.println("Adding data to Ontology....\n");

            OntologyBuilder builder = new OntologyBuilder(o, man, br, file);

            try {
                builder.build();
            } catch (Exception e) {
                System.err.println("Failed to add data to Ontology");
                return;
            }

            System.out.println("Generating SVG....\n");

            SVGGenerator svgGenerator;

            try {
                svgGenerator = new SVGGenerator(o, this.variablesTocolor);
                svgGenerator.generate(folderPath + '/' + listOfFiles[i]);
            } catch (Exception e) {
                e.printStackTrace();
                System.err.println("Failed to generate SVG");
                return;
            }

            System.out.println("-----------------SVG Generated----------------\n\n");
        }

    }
}
