package com.example.spring.demo.svg;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import java.awt.*;

public class Line extends SVGElement {
    private final int x1;
    private final int y1;
    private final int x2;
    private final int y2;
    private Element line;
    private final Color c;
    private final String name;

    public Line(int x1, int y1, int x2, int y2, Color c, String name, Document document, Element root) {
        super(document, root);
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
        this.c = c;
        this.name = name;
    }

    public void draw() {
        line = document.createElement("line");
        root.appendChild(line);

        line.setAttribute("class", name);
        line.setAttribute("x1", String.valueOf(x1));
        line.setAttribute("y1", String.valueOf(y1));
        line.setAttribute("x2", String.valueOf(x2));
        line.setAttribute("y2", String.valueOf(y2));
        line.setAttribute("stroke-width", "3");
        line.setAttribute("stroke", "rgb(" + c.getRed() + "," + c.getGreen() + "," + c.getBlue() + ")");

        if (y1 == y2) {
            Element g = document.createElement("g");
            g.setAttribute("id", name);
            g.setAttribute("display", "none");
            root.appendChild(g);
            Element element = document.createElement("rect");
            g.appendChild(element);

            element.setAttribute("x", String.valueOf(x1 + (x2 - x1) / 2 - 40));
            element.setAttribute("y", String.valueOf(y1 - 15));
            element.setAttribute("width", String.valueOf(80));
            element.setAttribute("height", String.valueOf(30));
            element.setAttribute("stroke", "steelblue");
            element.setAttribute("stroke-width", "2");
            element.setAttribute("fill", "white");

            Element text = document.createElement("text");
            text.appendChild(document.createTextNode(name.toUpperCase()));
            g.appendChild(text);
            text.setAttribute("x", String.valueOf(x1 + (x2 - x1) / 2));
            text.setAttribute("y", String.valueOf(y1));
            text.setAttribute("dominant-baseline", "middle");
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("font-weight", "bold");
            text.setAttribute("font-size", "10");
        }


    }

    public void drawWithArrow() {
        draw();
        line.setAttribute("marker-end", "url(#triangle)");
    }

    public static Color generateRandomColor() {
        double hue = Math.random();
        int rgb = Color.HSBtoRGB((float) hue, 1, (float) 0.8);
        return new Color(rgb);
    }

    public int getX1() {
        return x1;
    }

    public int getY1() {
        return y1;
    }

    public int getX2() {
        return x2;
    }

    public int getY2() {
        return y2;
    }

}

