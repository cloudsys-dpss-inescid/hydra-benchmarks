#include <stdio.h>
#include "com_hello_jni_HelloJNI.h"

JNIEXPORT void JNICALL Java_com_hello_jni_HelloJNI_printHello(JNIEnv *env, jobject obj) {
    fprintf(stderr, "Hello World!\n");
    return;
}
