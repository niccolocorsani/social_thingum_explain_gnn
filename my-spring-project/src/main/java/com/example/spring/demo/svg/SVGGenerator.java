package com.example.spring.demo.svg;

import com.github.owlcs.ontapi.Ontology;
import org.apache.jena.query.*;
import org.apache.jena.rdf.model.RDFNode;
import org.semanticweb.owlapi.model.OWLOntology;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.awt.*;
import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.lang.Boolean.FALSE;
import static java.lang.Boolean.TRUE;

public class SVGGenerator {
    private final OWLOntology o;
    private ArrayList<String> flows;
    private final Document document;
    private final Element root;
    private String imageName;
    private List<String> variablesTocolor;

    public SVGGenerator(OWLOntology o, List<String> variablesTocolor) throws ParserConfigurationException {
        this.o = o;
        this.variablesTocolor = variablesTocolor;
        DocumentBuilderFactory documentFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder documentBuilder = documentFactory.newDocumentBuilder();
        document = documentBuilder.newDocument();
        root = document.createElement("svg");

      document.appendChild(root);

    }

    public void generate(String text) throws Exception {

        this.imageName = text;
        Map<String, Device> devices = drawDevices();
        drawFlows(devices);


        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "2");

        DOMSource domSource = new DOMSource(document);
        String fileName = text.replace("./directory", "./generated_svg").replace(".csv", ".svg");
        System.err.println(fileName);
        StreamResult streamResult = new StreamResult(new File(fileName));
        transformer.transform(domSource, streamResult);

    }

  private Map<String, Device> drawDevices() {
    ArrayList<String> querySensors;
    String unitOfMeasure;
    Map<String, Device> devices = new HashMap<>();

    ArrayList<String> queryDevices = runQuery("?subject rdf:type ?type. ?type rdfs:subClassOf* s:PhysicalObject . FILTER NOT EXISTS { ?subject rdf:type s:Sensor}");
    flows = runQuery("?subject rdf:type ?type. ?type rdfs:subClassOf* :Flow");

    int nUp = (int) Math.ceil((float) queryDevices.size() / 2);
    root.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    root.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
    root.setAttribute("width", "100%");
    root.setAttribute("height", "100%");
    root.setAttribute("viewBox", "0 0 " + ((nUp == queryDevices.size() / 2 ? 200 : 150) + nUp * 200) + " " + (330 + flows.size() * 10));
    createMarker();




    for (int i = 0; i < queryDevices.size(); i++) {
      ArrayList<ArrayList<String>> sensors = new ArrayList<>();

      querySensors = runQuery("?subject s:isContainedIn s:" + queryDevices.get(i) + " . ?subject rdf:type s:Sensor");
      ////TODO siccome le info aggiunte stanno nel prefix : e non s: riguardare questo worlaround
      querySensors.addAll(runQuery("?subject s:isContainedIn :" + queryDevices.get(i) + " . ?subject rdf:type s:Sensor"));
      querySensors.addAll(runQuery("?subject s:isContainedIn r:" + queryDevices.get(i) + " . ?subject rdf:type s:Sensor"));
      ////TODO siccome le info aggiunte stanno nel prefix : e non s: riguardare questo worlaround


      for (String s : querySensors) {
        ArrayList<String> sensorAndUnit = new ArrayList<>();
        // unitOfMeasure = runQuery("s:" + s + " :canMeasureIn ?subject").get(0); prima
        unitOfMeasure = runQuery("r:" + s + " :canMeasureIn ?subject").get(0);

        sensorAndUnit.add(s);
        sensorAndUnit.add(unitOfMeasure);
        sensors.add(sensorAndUnit);
      }

      ///// Questo if serve per posizionare gli elementi che se sono tanti (come si osserva sotto)
      // saranno posizionati in maniera differente


      // TODO così non può funzionare dal momento che  in ogni caso i dati saranno presi dall'ontologia (che contiene tutti, tranne l'ultimo). A sto punto tutti prenderanno il colore dell'ultimo analizzato
      String colorFill = "";
             /*
            String nome = queryDevices.get(i);
            Schermate schermate = new Schermate();

            if (schermate.Carico.toLowerCase().contains(queryDevices.get(i) ))
                colorFill = "#FF5733";
            else if
            (schermate.Carico2.toLowerCase().contains(queryDevices.get(i) ))
                colorFill = "aliceblue";
            else if (schermate.FeCl3.toLowerCase().contains(queryDevices.get(i) ))
                colorFill = "#FFF633";
            else if (schermate.Ferroso.toLowerCase().contains(queryDevices.get(i) ))
                colorFill = "#75FF33";
            else colorFill = "aliceblue";*/
      colorFill = "aliceblue";


      if (i < nUp) {
        devices.put(queryDevices.get(i), new Device(100 + i * 200, 100, 1, queryDevices.get(i), sensors, document, root, colorFill));
      } else {
        devices.put(queryDevices.get(i), new Device(177 + (i % nUp) * 200, 300, 2, queryDevices.get(i), sensors, document, root, colorFill));
      }

    }

    return devices;
  }

  private void drawFlows(Map<String, Device> devices) throws Exception {
    ArrayList<String> queryStartDevices;
    ArrayList<String> queryEndDevices;
    int numberOfFlowsUP = 0;
    int numberOfFlowsMiddle = 0;
    int numberOfFlowsDown = 0;
    int n = 0;
    ArrayList<ArrayList<Device>> startAndEndDevices = new ArrayList<>();
    StringBuilder animationLines = new StringBuilder();
    StringBuilder animationDevices = new StringBuilder();

    for (String flow : flows) {
      ArrayList<Device> start = new ArrayList<>();
      ArrayList<Device> end = new ArrayList<>();
      queryStartDevices = runQuery(":" + flow + " :startIn ?subject . ?subject rdf:type ?type. ?type rdfs:subClassOf* s:PhysicalObject");
      //TODO aggiunta
      queryStartDevices.addAll(runQuery("r:" + flow + " :startIn ?subject . ?subject rdf:type ?type. ?type rdfs:subClassOf* s:PhysicalObject"));

      queryEndDevices = runQuery(":" + flow + " :endIn ?subject . ?subject rdf:type ?type. ?type rdfs:subClassOf* s:PhysicalObject");

      //TODO aggiunta
      queryEndDevices.addAll(runQuery("r:" + flow + " :endIn ?subject . ?subject rdf:type ?type. ?type rdfs:subClassOf* s:PhysicalObject"));

      int k = 0;
      int l = 0;


      for (String s : queryStartDevices) {
        start.add(devices.get(s));

        if (l == 0) {
          animationDevices.append("[\"").append(s).append("\", ");
        } else {
          animationDevices.append("\"").append(s).append("\", ");
        }
        l++;

      }

      for (String e : queryEndDevices) {
        end.add(devices.get(e));

        if (k < queryEndDevices.size() - 1) {
          animationDevices.append("\"").append(e).append("\", ");
        } else {
          animationDevices.append("\"").append(e).append("\"]");
        }
        k++;
      }

      if (n < flows.size() - 1) {
        animationLines.append("\"").append(flow).append("\"").append(", ");
        animationDevices.append(", ");
      } else {
        animationLines.append("\"").append(flow).append("\"");
      }
      n++;

      startAndEndDevices.add(start);
      startAndEndDevices.add(end);

      if(start.isEmpty())
        System.out.println("dl");

      if (areAllSameLevel(start, end)) {
        if (start.get(0).getLevel() == 1) {
          numberOfFlowsUP++;
        } else {
          numberOfFlowsDown++;
        }
      } else {
        numberOfFlowsMiddle++;
      }
    }

    SpaceController scUp = new SpaceController(20, 20 + numberOfFlowsUP * 10, numberOfFlowsUP, SpaceController.DECREASE);
    SpaceController scMiddle = new SpaceController(170 + numberOfFlowsUP * 10, 170 + numberOfFlowsUP * 10 + numberOfFlowsMiddle * 10, numberOfFlowsMiddle, SpaceController.INCREASE);
    SpaceController scDown = new SpaceController(310 + numberOfFlowsUP * 10 + numberOfFlowsMiddle * 10, 310 + numberOfFlowsUP * 10 + numberOfFlowsMiddle * 10 + numberOfFlowsDown * 10, numberOfFlowsDown, SpaceController.INCREASE);

    int finalNumberOfFlowsUP = numberOfFlowsUP;
    int finalNumberOfFlowsMiddle = numberOfFlowsMiddle;

    devices.forEach((name, device) -> {
      if (device.getLevel() == 1) {
        device.setY(40 + finalNumberOfFlowsUP * 10);
      } else {
        device.setY(190 + finalNumberOfFlowsUP * 10 + finalNumberOfFlowsMiddle * 10);
      }
      device.draw();
    });

    for (int i = 0; i < flows.size(); i++) {
      ArrayList<String> colorArray = runQuery(":" + flows.get(i) + " :color ?subject");




      String color;
      if (colorArray.size() == 1) {
        color = colorArray.get(0);
      } else {
        color = "#000000";
      }
      if (areAllSameLevel(startAndEndDevices.get(i * 2), startAndEndDevices.get(i * 2 + 1))) {
        if (startAndEndDevices.get(i * 2).get(0).getLevel() == 1) {
          upBuilder(scUp, startAndEndDevices.get(i * 2), startAndEndDevices.get(i * 2 + 1), flows.get(i), color);
        } else {
          downBuilder(scDown, startAndEndDevices.get(i * 2), startAndEndDevices.get(i * 2 + 1), flows.get(i), color);
        }
      } else {
        middleBuilder(scMiddle, startAndEndDevices.get(i * 2), startAndEndDevices.get(i * 2 + 1), flows.get(i), color);
      }
    }

    for (String flow : flows) {
      Element element = document.createElement("use");
      element.setAttribute("xlink:href", "#" + flow);
      root.appendChild(element);
    }

    animate(animationLines.toString(), animationDevices.toString());

  }

  //// Qui solo il javascript
  private void animate(String animationLines, String animationDevices) {
    String javascript = "\nvar lines = [" + animationLines + "];\n" +
      "var devices = [" + animationDevices + "];\n" +
      "var elementLines = [];\n" +
      "var elementDevices = [];\n" +
      "var n = [];\n" +
      "var nD = [];\n" +
      "function highlight(className, value, display) {\n" +
      "    document.getElementById(className.baseVal).setAttribute(\"display\", display);\n" +
      "    for(var i = 0; i <  n[className.baseVal]; i ++) {\n" +
      "        elementLines[className.baseVal][i].setAttribute(\"stroke-width\", value);\n" +
      "    }\n" +
      "    for(var i = 0; i < nD[className.baseVal]; i++) {\n" +
      "        elementDevices[className.baseVal][i].setAttribute(\"stroke-width\", value);\n" +
      "    }\n" +
      "}\n" +
      "for(var i = 0; i < lines.length; i++) {\n" +
      "    var currentClass = lines[i];\n" +
      "    elementLines[currentClass] = document.getElementsByClassName(currentClass);\n" +
      "    n[currentClass] = elementLines[currentClass].length;\n" +
      "    nD[currentClass] = devices[i].length;\n" +
      "    elementDevices[currentClass] = [];\n" +
      "    for(var j = 0; j < nD[currentClass]; j++) {\n" +
      "        elementDevices[currentClass][j] = document.getElementById(devices[i][j]);\n" +
      "    }\n" +
      "    for(var k = 0; k < n[currentClass]; k++) {\n" +
      "        elementLines[currentClass][k].onmouseover = function() {\n" +
      "            highlight(this.className, \"7\", \"block\");\n" +
      "        };\n" +
      "        elementLines[currentClass][k].onmouseout = function() {\n" +
      "            highlight(this.className, \"3\", \"none\");\n" +
      "        };\n" +
      "    }\n" +
      "};";

    Element script = document.createElement("script");
    script.appendChild(document.createTextNode(javascript));
    script.setAttribute("type", "text/javascript");
    root.appendChild(script);


  }

  private ArrayList<String> runQuery(String query) {
    ArrayList<String> arrayList = new ArrayList<>();
    try (QueryExecution qexec = QueryExecutionFactory.create(QueryFactory
      .create("PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
        "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
        "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n" +
        "PREFIX : <http://www.disit.org/saref4bldg-ext/>\n" +
        "PREFIX s: <https://saref.etsi.org/saref4bldg/>\n" +
        "PREFIX c: <https://saref.etsi.org/core/>\n" +
        "PREFIX r: <http://www.disit.org/altair/resource/>\n" +

        "SELECT ?subject WHERE {" + query + "}"), ((Ontology) o).asGraphModel())) {
      ResultSet res = qexec.execSelect();
      while (res.hasNext()) {
        QuerySolution qs = res.nextSolution();
        RDFNode x = qs.get("subject");
        if (x.asNode().isURI()) {
          arrayList.add(x.asNode().getLocalName());
        } else if (x.asNode().isLiteral()) {
          arrayList.add(x.asNode().getLiteral().toString());
        }
      }
    }
    return arrayList;
  }

  private void createMarker() {
    Element marker = document.createElement("marker");
    root.appendChild(marker);

    marker.setAttribute("id", "triangle");
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "7");
    marker.setAttribute("refY", "5");
    marker.setAttribute("fill", "rgb(255,60,60)");
    marker.setAttribute("markerWidth", "4");
    marker.setAttribute("markerHeight", "4");
    marker.setAttribute("orient", "auto");

    Element path = document.createElement("path");
    marker.appendChild(path);

    path.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");

    marker.setAttribute("id", "triangle");
  }

  private void middleBuilder(SpaceController spaceController, ArrayList<Device> start, ArrayList<Device> end, String name, String colorString) throws Exception {
    Color color = Color.decode(colorString);
    ArrayList<Device> all = new ArrayList<>();
    all.addAll(start);
    all.addAll(end);
    int x1 = min(all, "middle");
    int x2 = max(all, "middle");
    int y = spaceController.next();
    Line line = new Line(x1 - 2, y, x2 + 2, y, color, name, document, root);
    line.draw();

    for (Device device : start) {
      if (device.getLevel() == 1) {
        x1 = device.getNextPosition("down");
        line = new Line(x1, device.getY() + device.getHeight(), x1, y + 2, color, name, document, root);
      } else {
        x1 = device.getNextPosition("up");
        line = new Line(x1, y - 2, x1, device.getY(), color, name, document, root);
      }
      line.draw();
    }

    for (Device device : end) {
      if (device.getLevel() == 1) {
        x1 = device.getNextPosition("down");
        line = new Line(x1, y + 2, x1, device.getY() + device.getHeight(), color, name, document, root);
      } else {
        x1 = device.getNextPosition("up");
        line = new Line(x1, y - 2, x1, device.getY(), color, name, document, root);
      }
      line.drawWithArrow();
    }

  }

  private void upBuilder(SpaceController spaceController, ArrayList<Device> start, ArrayList<Device> end, String name, String colorString) throws Exception {
    Color color = Color.decode(colorString);
    ArrayList<Device> all = new ArrayList<>();
    all.addAll(start);
    all.addAll(end);
    int x1 = min(all, "up");
    int x2 = max(all, "up");
    int y = spaceController.next();
    Line line = new Line(x1 - 2, y, x2 + 2, y, color, name, document, root);
    line.draw();

    for (Device device : start) {
      x1 = device.getNextPosition("up");
      line = new Line(x1, y - 2, x1, device.getY(), color, name, document, root);
      line.draw();
    }

    for (Device device : end) {
      x1 = device.getNextPosition("up");
      line = new Line(x1, y - 2, x1, device.getY(), color, name, document, root);
      line.drawWithArrow();
    }

  }

  private void downBuilder(SpaceController spaceController, ArrayList<Device> start, ArrayList<Device> end, String name, String colorString) throws Exception {
    Color color = Color.decode(colorString);
    ArrayList<Device> all = new ArrayList<>();
    all.addAll(start);
    all.addAll(end);
    int x1 = min(all, "down");
    int x2 = max(all, "down");
    int y = spaceController.next();
    Line line = new Line(x1 - 2, y, x2 + 2, y, color, name, document, root);
    line.draw();

    for (Device device : start) {
      x1 = device.getNextPosition("down");
      line = new Line(x1, y + 2, x1, device.getY() + device.getHeight(), color, name, document, root);
      line.draw();
    }

    for (Device device : end) {
      x1 = device.getNextPosition("down");
      line = new Line(x1, y + 2, x1, device.getY() + device.getHeight(), color, name, document, root);
      line.drawWithArrow();
    }

  }

  private int min(ArrayList<Device> arrayList, String position) {
    if (position.equals("middle")) {
      if (arrayList.get(0).getLevel() == 1) {
        position = "down";
      } else {
        position = "up";
      }
      int min = arrayList.get(0).getCurrentPosition(position);

      for (Device device : arrayList) {
        if (device.getLevel() == 1) {
          position = "down";
        } else {
          position = "up";
        }
        if (device.getCurrentPosition(position) < min) {
          min = device.getCurrentPosition(position);
        }
      }
      return min;
    } else {
      int min = arrayList.get(0).getCurrentPosition(position);

      for (Device device : arrayList) {
        if (device.getCurrentPosition(position) < min) {
          min = device.getCurrentPosition(position);
        }
      }
      return min;
    }
  }

  private int max(ArrayList<Device> arrayList, String position) {
    if (position.equals("middle")) {
      if (arrayList.get(0).getLevel() == 1) {
        position = "down";
      } else {
        position = "up";
      }
      int max = arrayList.get(0).getCurrentPosition(position);

      for (Device device : arrayList) {
        if (device.getLevel() == 1) {
          position = "down";
        } else {
          position = "up";
        }
        if (device.getCurrentPosition(position) > max) {
          max = device.getCurrentPosition(position);
        }
      }
      return max;
    } else {
      int max = arrayList.get(0).getCurrentPosition(position);

      for (Device device : arrayList) {
        if (device.getCurrentPosition(position) > max) {
          max = device.getCurrentPosition(position);
        }
      }
      return max;
    }
  }

  private boolean areAllSameLevel(ArrayList<Device> start, ArrayList<Device> end) {
    ArrayList<Device> all = new ArrayList<>();
    all.addAll(start);
    all.addAll(end);

    for (int i = 0; i < all.size() - 1; i++) {
      if (all.get(i).getLevel() != all.get(i + 1).getLevel()) {
        return FALSE;
      }
    }
    return TRUE;
  }


}
