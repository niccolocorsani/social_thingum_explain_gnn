package com.example.spring.demo.svg;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class Sensor extends SVGElement {
  private final int x;
  private final int y;
  private final String name;
  private final String unitOfMeasure;
  private final int width;
  private final int height;


  public Sensor(String name, String unitOfMeasure, int x, int y, int width, int height, Document document, Element root) {
    super(document, root);
    this.x = x;
    this.y = y;
    this.name = name;
    this.unitOfMeasure = unitOfMeasure;
    this.width = width;
    this.height = height;
  }

  public void draw() {
    Element element = document.createElement("rect");
    root.appendChild(element);

    element.setAttribute("x", String.valueOf(x));
    element.setAttribute("y", String.valueOf(y));
    element.setAttribute("width", String.valueOf(width));


    element.setAttribute("height", String.valueOf(height));
    element.setAttribute("stroke", "steelblue");
    element.setAttribute("stroke-width", "2");
    element.setAttribute("fill", "white");

    element = document.createElement("text");
    element.appendChild(document.createTextNode(name + ":"));
    root.appendChild(element);
    element.setAttribute("x", String.valueOf(x + 5));
    element.setAttribute("y", String.valueOf(y + height / 2));
    element.setAttribute("dominant-baseline", "middle");
    element.setAttribute("font-size", "12");

    element = document.createElement("text");
    element.appendChild(document.createTextNode("100"));
    root.appendChild(element);
    element.setAttribute("x", String.valueOf(x + width / 1.5));
    element.setAttribute("y", String.valueOf(y + height / 2));
    element.setAttribute("dominant-baseline", "middle");
    element.setAttribute("text-anchor", "middle");
    element.setAttribute("font-size", "12");
    element.setAttribute("data-siow", "[  {   \"event\": \"s4csvg_" + name + "\",   \"originator\": \"server\",   \"actions\": [    {     \"input\": \"$.lastValue\",     \"target\": \"textContent\" }  ]  } ]");

    element = document.createElement("text");
    element.appendChild(document.createTextNode(unitOfMeasure));
    root.appendChild(element);
    element.setAttribute("x", String.valueOf(x + width / 1.2));
    element.setAttribute("y", String.valueOf(y + height / 2));
    element.setAttribute("dominant-baseline", "middle");
    element.setAttribute("font-size", "12");
  }

  public String getName() {
    return name;
  }
}
