package com.example.spring.demo.svg;

import com.github.owlcs.ontapi.OntManagers;
import org.apache.commons.io.input.BOMInputStream;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;

import javax.swing.*;
import java.io.*;


public class AsyncExecution extends Thread {
    private final JTextArea textArea;
    private final JTextField t1, t2;
    private final JButton b;

    public AsyncExecution(JTextField t1, JTextField t2, JButton b, JTextArea textArea) {
        this.textArea = textArea;
        this.t1 = t1;
        this.t2 = t2;
        this.b = b;
    }

    @Override
    public void run() {
        textArea.append("--------------------Starting------------------\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());
        InputStream inputStream;


        try {
            inputStream = new FileInputStream(t1.getText());
        } catch (FileNotFoundException fileNotFoundException) {
            textArea.append("Invalid CSV File!\n");
            textArea.setCaretPosition(textArea.getDocument().getLength());
            b.setEnabled(true);
            return;
        }

        textArea.append("Parsing CSV....\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());

        BOMInputStream bOMInputStream = new BOMInputStream(inputStream);
        InputStreamReader reader = new InputStreamReader(new BufferedInputStream(bOMInputStream));
        BufferedReader br = new BufferedReader(reader);

        OWLOntologyManager man = OntManagers.createONT();
        File file = new File(t2.getText());
        OWLOntology o;

        textArea.append("Loading Ontology...\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());

        try {
            o = man.loadOntologyFromOntologyDocument(file);
        } catch (OWLOntologyCreationException e) {
            textArea.append("Invalid OWL File!\n");
            textArea.setCaretPosition(textArea.getDocument().getLength());
            b.setEnabled(true);
            return;
        }

        textArea.append("Adding data to Ontology....\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());

        OntologyBuilder builder = new OntologyBuilder(o, man, br, file);

        try {
            builder.build();
        } catch (Exception e) {
            textArea.append("Failed to add data to Ontology");
            textArea.setCaretPosition(textArea.getDocument().getLength());
            return;
        }

        textArea.append("Generating SVG....\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());

        SVGGenerator svgGenerator;

        try {
            svgGenerator = new SVGGenerator(o, null);
            svgGenerator.generate(t1.getText());
        } catch (Exception e) {
            e.printStackTrace();
            //logger.debug(e.getMessage());
            textArea.append("Failed to generate SVG");
            textArea.setCaretPosition(textArea.getDocument().getLength());
            return;
        }

        textArea.append("-----------------SVG Generated----------------\n\n");
        textArea.setCaretPosition(textArea.getDocument().getLength());

        b.setEnabled(true);

    }
}
