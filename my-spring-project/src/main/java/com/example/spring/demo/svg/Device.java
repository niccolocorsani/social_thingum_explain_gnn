package com.example.spring.demo.svg;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import java.util.ArrayList;


public class Device extends SVGElement {
    private final int x;
    private int y;
    private final int level;
    private final String name;
    private final ArrayList<ArrayList<String>> sensors;
    private final SpaceController scUP;
    private final SpaceController scDown;
    private final int width = 150;
    private final int height = 100;
    private final int numberOfFlows = 10;
    private String fillColor;

    public Device(int x, int y, int level, String name, ArrayList<ArrayList<String>> sensors, Document document, Element root,String fillColor) {
        super(document, root);
        this.fillColor = fillColor;
        this.x = x;
        this.y = y;
        this.level = level;
        this.name = name;
        this.sensors = sensors;
        scUP = new SpaceController(x + 5, x + width - 5, numberOfFlows, SpaceController.INCREASE);
        scDown = new SpaceController(x + 5, x + width - 5, numberOfFlows, SpaceController.INCREASE);
    }

    public void draw() {
        Element rectangle = document.createElement("rect");
        root.appendChild(rectangle);

        rectangle.setAttribute("id", name);
        rectangle.setAttribute("x", String.valueOf(x));
        rectangle.setAttribute("y", String.valueOf(y));
        rectangle.setAttribute("width", String.valueOf(width));
        rectangle.setAttribute("height", String.valueOf(height));
        rectangle.setAttribute("stroke", "skyblue");
        rectangle.setAttribute("stroke-width", "3");
        rectangle.setAttribute("fill", this.fillColor);

        Element text = document.createElement("text");
        text.appendChild(document.createTextNode(name.toUpperCase()));
        root.appendChild(text);
        text.setAttribute("x", String.valueOf(x + width / 2));
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-weight", "bold");

        if(sensors.size() == 0){
            text.setAttribute("y", String.valueOf(y + height/2));
        }else{
            text.setAttribute("y", String.valueOf(y + 15));
        }

        Sensor sensor;
        for (int i = 0; i < sensors.size(); i++) {
            if (sensors.size() == 1) {
                sensor = new Sensor(sensors.get(i).get(0), sensors.get(i).get(1), x + 5, y + 35, width - 10, (height - 30) / 2, document, root);
            } else {
                sensor = new Sensor(sensors.get(i).get(0), sensors.get(i).get(1), x + 5, y + 25 + i * (height - 30) / sensors.size(), width - 10, (height - 30) / sensors.size(), document, root);
            }
            sensor.draw();
        }

    }

    public int getNextPosition(String position) throws Exception {
        if (position.equals("up")) {
            return scUP.next();
        } else {
            return scDown.next();
        }
    }

    public int getCurrentPosition(String position) {
        if (position.equals("up")) {
            return scUP.getCurrent();
        } else {
            return scDown.getCurrent();
        }
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public String getName() {
        return name;
    }

    public int getLevel() {
        return level;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public void setY(int y) {
        this.y = y;
    }
}

