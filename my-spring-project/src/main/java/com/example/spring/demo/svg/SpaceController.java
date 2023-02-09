package com.example.spring.demo.svg;

import static java.lang.Boolean.FALSE;
import static java.lang.Boolean.TRUE;

public class SpaceController {
    private final int start;
    private final int end;
    private int current;
    private final int step;
    private final boolean mode;
    public static final boolean INCREASE = TRUE;
    public static final boolean DECREASE = FALSE;

    protected SpaceController(int start, int end, int parts, boolean mode) {
        this.start = start;
        this.end = end;
        this.mode = mode;
        if (parts != 0) {
            step = (end - start) / parts;
        } else {
            step = 0;
        }

        if (mode) {
            this.current = start;
        } else {
            this.current = end;
        }
    }

    public int next() throws Exception {
        int tmp = current;
        if (mode) {
            current = current + step;
            if (current > end) {
                //TODO riguardare
            //    throw new Exception();
            }
        } else {
            current = current - step;
            if (current < start) {
                //TODO riguardare
                //    throw new Exception();
            }
        }
        return tmp;
    }

    public int getCurrent() {
        return current;
    }
}
