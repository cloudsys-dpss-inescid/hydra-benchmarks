package com.dbread;

import java.util.HashMap;
import java.util.Map;

import com.oracle.svm.graalvisor.guestapi.jdbc.HostedConnection;
import com.oracle.svm.graalvisor.guestapi.jdbc.HostedConnection.HostedResultSet;
import com.oracle.svm.graalvisor.guestapi.jdbc.HostedConnection.HostedResultSetMetaData;
import com.oracle.svm.graalvisor.guestapi.jdbc.HostedConnection.HostedStatement;

public class DbRead {

    private static final String DB_URL = "jdbc:postgresql://127.0.0.1:5432/jdbc_experiment";
    private static final String USER = "postgres";
    private static final String PASS = "0000";
    private static final String QUERY = "SELECT id, manufacturer, model FROM cars FETCH FIRST %d ROWS ONLY";

    private static final HostedConnection conn = HostedConnection.getConnection(DB_URL, USER, PASS);

    public static Map<String, Object> main(Map<String, Object> input) {
        Object iterationsObject = input.get("iterations");
        int iterations = 5;
        if (iterationsObject != null) {
            iterations = Integer.valueOf((String) iterationsObject);
        }

        warmup(iterations);

        Map<String, Object> output = new HashMap<>();

        for (int rows = 2; rows <= 16384; rows *= 2) {
            long[] res = readDatabase(iterations, rows);
            output.put(Integer.toString(rows), res);
        }
        return output;
    }

    private static void warmup(int iterations) {
        readDatabase(iterations, iterations);
    }

    private static long[] readDatabase(int iterations, int rows) {
        long[] executionTimes = new long[iterations];

        for (int i = 0; i < iterations; ++i) {
            HostedStatement stmt = conn.createStatement();
            long before = System.nanoTime();
            HostedResultSet rs = stmt.executeQuery(String.format(QUERY, rows));
            String result = resultSetToString(rs);
            long after = System.nanoTime();
            // conn.release();
            stmt.close();
            rs.close();
            executionTimes[i] = after - before;
            System.gc();
        }

        return executionTimes;
    }

    private static String resultSetToString(HostedResultSet rs) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        sb.append(System.getProperty("line.separator"));
        HostedResultSetMetaData metaData = rs.getMetaData();
        int nColumns = metaData.getColumnCount();
        while (rs.next()) {
            sb.append("[");
            for (int i = 1; i <= nColumns; ++i) {
                sb.append(metaData.getColumnName(i));
                sb.append(" = ");
                sb.append(rs.getString(i));
                if (i < nColumns) {
                    sb.append(", ");
                }
            }
            sb.append("]");
            sb.append(System.getProperty("line.separator"));
        }
        sb.append("}");
        return sb.toString();
    }

}
