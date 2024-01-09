#include <stdio.h>
#include <unistd.h>
#include "com_jni_HelloJNI.h"

JNIEXPORT void JNICALL Java_com_jni_HelloJNI_printHello8(JNIEnv *env, jobject obj) {
    fprintf(stderr, "Hello World 8!\n");
    return;
}
