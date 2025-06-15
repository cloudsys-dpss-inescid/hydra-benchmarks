package com.oracle.graalos.workload;

import java.util.Map;

public interface Workload {

    Map<String, Object> invoke(Map<String, Object> args);

}
