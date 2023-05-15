package com.odd_even;

import com.oracle.svm.core.annotate.AutomaticFeature;
import org.graalvm.nativeimage.hosted.Feature;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

@AutomaticFeature
public class PrintNativeMethodsFeature implements Feature {

    List<Method> nativeMethods = new LinkedList<>();

    @Override
    public void beforeAnalysis(BeforeAnalysisAccess access) {

        access.registerSubtypeReachabilityHandler(
                (duringAnalysisAccess, clazz) -> {
                    nativeMethods.addAll(Arrays.stream(clazz.getDeclaredMethods())
                            .filter(method -> Modifier.isNative(method.getModifiers()))
                            .collect(Collectors.toList()));
                },
                Object.class);

        System.out.println("\nRegister Reachability Handler Success.\n");
    }

    @Override
    public void afterAnalysis(AfterAnalysisAccess access) {
        nativeMethods.sort((method, other) -> {
            if (method.getDeclaringClass() != other.getDeclaringClass()) {
                return method.getDeclaringClass().getCanonicalName().compareTo(other.getDeclaringClass().getCanonicalName());
            } else {
                return method.getName().compareTo(other.getName());
            }
        });

        nativeMethods.stream().forEach(
                nativeMethod -> {
                    System.out.println(nativeMethod.getDeclaringClass().getCanonicalName() +
                    ": " +
                    nativeMethod.toString());
                });
    }
}
