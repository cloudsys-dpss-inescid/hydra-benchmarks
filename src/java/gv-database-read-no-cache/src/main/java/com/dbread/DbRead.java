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
    private static final String QUERY = "SELECT id, manufacturer, model FROM cars";

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
        Map<String, Object> output = new HashMap<>();
        try {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(QUERY);
            String result = resultSetToString(rs);
            // conn.release();
            stmt.close();
            rs.close();
            output.put("result", result.length());
        } catch (SQLException e) {
            output.put("result", e.getMessage());
        }
        return output;
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
