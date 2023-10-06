package org.graalvm.argo.dataset.execution;

import org.apache.commons.cli.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class SvmExecutorEntryPoint {

    public static void main(String[] args) {
        Options options = prepareOptions();
        try {
            CommandLine cmd = new DefaultParser().parse(options, args);
            String inputFilePath = cmd.getOptionValue("input");
            String functionCodeFilePath = cmd.getOptionValue("functionCode");
            String functionLanguage = cmd.getOptionValue("functionLanguage", "java");
            String functionEntryPoint = cmd.getOptionValue("functionEntryPoint");
            String gvSandbox = cmd.getOptionValue("gvSandbox", "isolate");
            String gvCache = cmd.getOptionValue("gvCache", "true");
            boolean debug = cmd.hasOption("debug");
            byte[] functionCode = Files.readAllBytes(Paths.get(functionCodeFilePath));
            String gvProxyAddress = cmd.getOptionValue("gvProxyAddress", "localhost:8080");
            ExecutorConfiguration config = new ExecutorConfiguration(functionCode, functionLanguage, functionEntryPoint, gvSandbox, gvCache, debug, gvProxyAddress);
            SvmInvocationTraceExecutor executor = new SvmInvocationTraceExecutor(config);
            executor.execute(inputFilePath);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            new HelpFormatter().printHelp("utility-name", options);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static Options prepareOptions() {
        Options options = new Options();
        Option input = new Option("i", "input", true, "Input invocation trace file path.");
        input.setRequired(true);
        options.addOption(input);
        Option functionCode = new Option("fc", "functionCode", true, "Function code file path.");
        functionCode.setRequired(true);
        options.addOption(functionCode);
        Option functionLanguage = new Option("fl", "functionLanguage", true, "Function language.");
        functionLanguage.setRequired(true);
        options.addOption(functionLanguage);
        Option functionEntryPoint = new Option("fep", "functionEntryPoint", true, "Function entry point.");
        functionEntryPoint.setRequired(true);
        options.addOption(functionEntryPoint);
        Option gvSandbox = new Option("gvs", "gvSandbox", true, "Sandbox to be used in Graalvisor.");
        gvSandbox.setRequired(false);
        options.addOption(gvSandbox);
        Option gvCache = new Option("gvc", "gvCache", true, "Cache isolates in Graalvisor.");
        gvCache.setRequired(false);
        options.addOption(gvCache);
        Option debug = new Option("d", "debug", false, "Just print requests instead of sending them.");
        debug.setRequired(false);
        options.addOption(debug);
        Option gvProxyAddress = new Option("pa", "gvProxyAddress", true, "Full address of the lambda manager.");
        gvProxyAddress.setRequired(false);
        options.addOption(gvProxyAddress);
        return options;
    }

}
