package com.example.spring.demo.svg;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public abstract class SVGElement {
    protected Document document;
    protected Element root;

    protected SVGElement(Document document, Element root) {
        this.document = document;
        this.root = root;
    }

    public abstract void draw();
}
