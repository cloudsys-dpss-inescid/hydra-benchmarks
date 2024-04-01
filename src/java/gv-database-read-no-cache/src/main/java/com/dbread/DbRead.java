package com.dbread;

import java.util.HashMap;
import java.util.Map;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Statement;
import java.sql.SQLException;
import java.sql.DriverManager;

public class DbRead {

    private static final String DB_URL = "jdbc:postgresql://127.0.0.1:5432/jdbc_experiment";
    private static final String USER = "postgres";
    private static final String PASS = "0000";
    private static final String QUERY = "SELECT id, manufacturer, model FROM cars FETCH FIRST %d ROWS ONLY";

    private static Connection conn;// = DriverManager.getConnection(DB_URL, USER, PASS);

    static {
        try {
            conn = DriverManager.getConnection(DB_URL, USER, PASS);
        } catch (SQLException e) {
            e.printStackTrace();
            conn = null;
        }
    }

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

        try {
            for (int i = 0; i < iterations; ++i) {
                Statement stmt = conn.createStatement();
                long before = System.nanoTime();
                ResultSet rs = stmt.executeQuery(String.format(QUERY, rows));
                String result = resultSetToString(rs);
                long after = System.nanoTime();
                stmt.close();
                rs.close();
                executionTimes[i] = after - before;
                System.gc();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return executionTimes;
    }

    private static String resultSetToString(ResultSet rs) throws SQLException {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        sb.append(System.getProperty("line.separator"));
        ResultSetMetaData metaData = rs.getMetaData();
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
