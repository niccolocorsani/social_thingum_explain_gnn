package com.example.spring.demo.svg;

import javax.swing.filechooser.FileFilter;
import java.io.File;

class FileTypeFilter extends FileFilter {
    private final String type;

    public FileTypeFilter(String type) {
        this.type = type;
    }

    public boolean accept(File file) {
        if (file.isDirectory()) return true;
        String name = file.getName().toLowerCase();
        return name.endsWith(type);
    }

    public String getDescription() {
        return "*." + type;
    }
}
